# 🏦 Account Management  Manages user accounts (create, update balance)
# """
#📌 Accounts API - Budget Buddy
#This module manages user bank accounts:
#✅ Create an account:       POST /accounts/create
#✅ Get account details:     GET /accounts/{account_id}
#✅ Update balance:          PUT /accounts/update_balance
#✅ List all accounts:       GET /accounts/list
#✅ Delete an account:       DELETE /accounts/{account_id}
#🔒 Security: JWT authentication required for all operations.
"""

# Step 1: Import Dependencies
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from auth import get_current_user
# Step 2: Define API Router
router = APIRouter(prefix="/accounts", tags=["Accounts"])
#Step 3: Create an Account
@router.post("/create")
def create_account(account_type: str, user: dict = Depends(get_current_user)):
    """
    Creates a new bank account (Checking/Savings) for the logged-in user.
    
    - account_type: "checking" or "savings"
    - user: Fetched from JWT token
    """
    if account_type not in ["checking", "savings"]:
        raise HTTPException(status_code=400, detail="Invalid account type")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO accounts (user_id, balance, account_type) VALUES (%s, %s, %s)",
                   (user["user_id"], 0.00, account_type))
    conn.commit()

    return {"message": f"{account_type.capitalize()} account created successfully"}

# Step 4: Fetch Account Details
@router.get("/{account_id}")
def get_account(account_id: int, user: dict = Depends(get_current_user)):
    """
    Fetches account details (balance, type) if it belongs to the logged-in user.
    
    - account_id: ID of the account
    - user: Authenticated user from JWT
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts WHERE account_id = %s AND user_id = %s", 
                   (account_id, user["user_id"]))
    account = cursor.fetchone()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found or unauthorized access")

    return account
 #Step 5: Update Account Balance
 @router.put("/update_balance")
def update_balance(account_id: int, amount: float, user: dict = Depends(get_current_user)):
    """
    Updates the balance of an account (used for deposits, withdrawals, and transfers).
    
    - account_id: ID of the account to modify
    - amount: Positive for deposits, negative for withdrawals
    - user: Authenticated user from JWT
    """
    if amount == 0:
        raise HTTPException(status_code=400, detail="Amount must be nonzero")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the account belongs to the user
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s AND user_id = %s", 
                   (account_id, user["user_id"]))
    account = cursor.fetchone()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found or unauthorized access")

    new_balance = account[0] + amount
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))
    conn.commit()

    return {"message": "Balance updated successfully", "new_balance": new_balance}
# Step 6: List All User Accounts
@router.get("/list")
def list_accounts(user: dict = Depends(get_current_user)):
    """
    Lists all accounts for the authenticated user.
    
    - user: Authenticated user from JWT
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user["user_id"],))
    accounts = cursor.fetchall()

    return {"accounts": accounts}
# Step 7: Delete an Account
@router.delete("/{account_id}")
def delete_account(account_id: int, user: dict = Depends(get_current_user)):
    """
    Deletes an account if the balance is zero and belongs to the user.
    
    - account_id: ID of the account to delete
    - user: Authenticated user from JWT
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the account exists and belongs to the user
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s AND user_id = %s", 
                   (account_id, user["user_id"]))
    account = cursor.fetchone()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found or unauthorized access")

    if account[0] != 0:
        raise HTTPException(status_code=400, detail="Cannot delete account with non-zero balance")

    # Delete account
    cursor.execute("DELETE FROM accounts WHERE account_id = %s", (account_id,))
    conn.commit()

    return {"message": "Account deleted successfully"}
