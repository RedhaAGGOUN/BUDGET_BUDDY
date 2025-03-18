#👨‍💼 Banker Features : Assigns clients to bankers, allows bankers to manage client accounts
# Import necessary libraries
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection  # Import database connection function
from auth import get_current_user  # Import authentication function

# Define the API router for banker-related routes
router = APIRouter(prefix="/banker", tags=["Banker"])

# ===============================
# 📌 Assign a Client to a Banker
# ===============================
@router.post("/assign_client")
def assign_client(client_id: int, user: dict = Depends(get_current_user)):
    """
    Assigns a client to the logged-in banker.

    - client_id: ID of the client to assign
    - user: Must be a banker (validated from JWT)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔍 Check if the logged-in user is a banker
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (user["user_id"],))
    role = cursor.fetchone()

    if not role or role[0] != "banker":
        raise HTTPException(status_code=403, detail="Only bankers can assign clients")

    # ✅ Assign the client to the banker
    cursor.execute("INSERT INTO banker_clients (banker_id, client_id) VALUES (%s, %s)",
                   (user["user_id"], client_id))
    conn.commit()

    return {"message": "Client assigned successfully"}

# ===============================
# 📌 View Assigned Clients
# ===============================
@router.get("/clients")
def get_assigned_clients(user: dict = Depends(get_current_user)):
    """
    Retrieves the list of clients assigned to the logged-in banker.
    
    - user: Must be authenticated and a banker
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔍 Check if the user is a banker
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (user["user_id"],))
    role = cursor.fetchone()

    if not role or role[0] != "banker":
        raise HTTPException(status_code=403, detail="Only bankers can view clients")

    # ✅ Retrieve the list of clients assigned to the banker
    cursor.execute("SELECT users.user_id, users.name, users.email FROM users "
                   "JOIN banker_clients ON users.user_id = banker_clients.client_id "
                   "WHERE banker_clients.banker_id = %s", (user["user_id"],))
    clients = cursor.fetchall()

    return {"clients": clients}

# ===============================================
# 📌 Banker Performing a Transaction for a Client
# ===============================================
@router.post("/transaction")
def banker_add_transaction(client_id: int, account_id: int, amount: float, transaction_type: str,
                           category: str, description: str, user: dict = Depends(get_current_user)):
    """
    Allows a banker to perform a transaction on behalf of a client.

    - client_id: The ID of the client
    - account_id: The account where the transaction is performed
    - amount: Amount of the transaction (must be positive for deposits)
    - transaction_type: "deposit", "withdrawal", or "transfer"
    - category: The category of the transaction (e.g., Rent, Food)
    - description: Details of the transaction
    - user: Must be a banker assigned to the client
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔍 Check if the logged-in user is a banker
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (user["user_id"],))
    role = cursor.fetchone()

    if not role or role[0] != "banker":
        raise HTTPException(status_code=403, detail="Only bankers can perform transactions")

    # 🔍 Ensure the banker is assigned to this client
    cursor.execute("SELECT * FROM banker_clients WHERE banker_id = %s AND client_id = %s",
                   (user["user_id"], client_id))
    assignment = cursor.fetchone()

    if not assignment:
        raise HTTPException(status_code=403, detail="Banker is not assigned to this client")

    # ✅ Perform the transaction on behalf of the client
    cursor.execute("INSERT INTO transactions (account_id, amount, transaction_type, category, description) "
                   "VALUES (%s, %s, %s, %s, %s)",
                   (account_id, amount, transaction_type, category, description))
    conn.commit()

    return {"message": "Transaction added by banker"}

# =======================================
# 📌 Remove a Client from a Banker's List
# =======================================
@router.delete("/remove_client")
def remove_client(client_id: int, user: dict = Depends(get_current_user)):
    """
    Removes a client from a banker’s assigned list.

    - client_id: The ID of the client to remove
    - user: Must be a banker
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔍 Check if the logged-in user is a banker
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (user["user_id"],))
    role = cursor.fetchone()

    if not role or role[0] != "banker":
        raise HTTPException(status_code=403, detail="Only bankers can remove clients")

    # ✅ Remove the client-banker relationship
    cursor.execute("DELETE FROM banker_clients WHERE banker_id = %s AND client_id = %s",
                   (user["user_id"], client_id))
    conn.commit()

    return {"message": "Client removed successfully"}
