# 💰 Transactions Handles deposits, withdrawals, transfers
# Import necessary libraries
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from auth import get_current_user

# Initialize API router
router = APIRouter(prefix="/transactions", tags=["Transactions"])

# =============================
# 📌 Create a Transaction (Deposit, Withdrawal, Transfer)
# =============================
@router.post("/add")
def add_transaction(account_id: int, amount: float, transaction_type: str, category: str, description: str, 
                    user: dict = Depends(get_current_user)):
    """
    Adds a new transaction to an account.

    - account_id: The ID of the account
    - amount: Transaction amount (must be positive)
    - transaction_type: "deposit", "withdrawal", or "transfer"
    - category: Category of the transaction (e.g., Food, Rent)
    - description: Additional transaction details
    - user: Must own the account
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔍 Verify that the account belongs to the logged-in user
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s AND user_id = %s",
                   (account_id, user["user_id"]))
    account = cursor.fetchone()

    if not account:
        raise HTTPException(status_code=403, detail="Unauthorized access to this account")

    balance = account[0]
    new_balance = balance + amount if transaction_type == "deposit" else balance - amount

    # ❌ Prevent overdraft (negative balance)
    if transaction_type == "withdrawal" and new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # ✅ Insert transaction into the database
    cursor.execute("INSERT INTO transactions (account_id, amount, transaction_type, category, description) "
                   "VALUES (%s, %s, %s, %s, %s)",
                   (account_id, amount, transaction_type, category, description))

    # ✅ Update account balance
    cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))

    conn.commit()
    return {"message": "Transaction added successfully", "new_balance": new_balance}

# =============================
# 📌 Get Transaction History (Filter by Date, Type, Category)
# =============================
@router.get("/history")
def get_transactions(account_id: int, start_date: str = None, end_date: str = None, 
                     category: str = None, transaction_type: str = None,
                     user: dict = Depends(get_current_user)):
    """
    Fetches the transaction history of an account, with optional filters.

    - account_id: The ID of the account
    - start_date: (Optional) Start date for filtering
    - end_date: (Optional) End date for filtering
    - category: (Optional) Filter transactions by category
    - transaction_type: (Optional) Filter by type ("deposit", "withdrawal", "transfer")
    - user: Must own the account
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔍 Verify account ownership
    cursor.execute("SELECT * FROM accounts WHERE account_id = %s AND user_id = %s",
                   (account_id, user["user_id"]))
    account = cursor.fetchone()

    if not account:
        raise HTTPException(status_code=403, detail="Unauthorized access to this account")

    # ✅ Build SQL query dynamically based on filters
    query = "SELECT * FROM transactions WHERE account_id = %s"
    params = [account_id]

    if start_date:
        query += " AND transaction_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND transaction_date <= %s"
        params.append(end_date)
    if category:
        query += " AND category = %s"
        params.append(category)
    if transaction_type:
        query += " AND transaction_type = %s"
        params.append(transaction_type)

    cursor.execute(query, tuple(params))
    transactions = cursor.fetchall()

    return {"transactions": transactions}

# =============================
# 📌 Delete a Transaction
# =============================
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, user: dict = Depends(get_current_user)):
    """
    Deletes a transaction if the user owns the account.

    - transaction_id: ID of the transaction to delete
    - user: Must own the associated account
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔍 Fetch transaction details
    cursor.execute("SELECT account_id, amount, transaction_type FROM transactions WHERE transaction_id = %s", 
                   (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    account_id, amount, transaction_type = transaction

    # 🔍 Verify account ownership
    cursor.execute("SELECT * FROM accounts WHERE account_id = %s AND user_id = %s",
                   (account_id, user["user_id"]))
    account = cursor.fetchone()

    if not account:
        raise HTTPException(status_code=403, detail="Unauthorized access to this transaction")

    # ✅ Adjust account balance before deleting transaction
    balance = account[2]  # Current balance
    new_balance = balance - amount if transaction_type == "deposit" else balance + amount

    cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
    cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))

    conn.commit()
    return {"message": "Transaction deleted successfully", "new_balance": new_balance}
