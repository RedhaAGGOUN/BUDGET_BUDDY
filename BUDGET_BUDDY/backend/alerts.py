# 📢 Alerts & Notifications : Generates alerts for overdrafts, large transactions, etc.
#This module manages user notifications, including:
#✅ Creating alerts (e.g., overdraft warnings, large transactions)
#✅ Retrieving unread alerts
#✅ Marking alerts as read
# Step 1: Import Dependencies
#APIRouter creates modular API routes for alerts.
#get_db_connection() handles MySQL connections.
#get_current_user() ensures only authenticated users can see alerts.
#from fastapi import APIRouter, HTTPException, Depends
#from database import get_db_connection
#from auth import get_current_user
#router = APIRouter(prefix="/alerts", tags=["Alerts"])
#@router.post("/create")  # Create a new alert
#@router.get("/unread")  # Get unread alerts
#@router.put("/mark_as_read/{alert_id}")  # Mark an alert as read
#@router.delete("/delete_read")  # Delete all read alerts


from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from auth import get_current_user
# Step 2: Define API Router
#prefix="/alerts" groups all alert-related endpoints under /alerts/....
#tags=["Alerts"] makes API documentation easier to read.
router = APIRouter(prefix="/alerts", tags=["Alerts"])
#Step 3: Create an Alert (/alerts/create)
#✅ How it works?
#1️⃣ Inserts a new unread alert into MySQL.
#2️⃣ Links the alert to the correct user (user_id).
#3️⃣ Returns a success message after creation.
@router.post("/create")
def create_alert(message: str, user_id: int):
    """
    Creates a new alert for a user.
    
    - message: Alert content
    - user_id: User who will receive the alert
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO alerts (user_id, message, is_read) VALUES (%s, %s, FALSE)", 
                   (user_id, message))
    conn.commit()

    return {"message": "Alert created successfully"}
#📂 Step 4: Fetch Unread Alerts (/alerts/unread)
#✅ How it works?
#1️⃣ Ensures the user is authenticated (Depends(get_current_user)).
#2️⃣ Fetches only unread alerts from MySQL.
#3️⃣ Returns a list of alerts (if any).
@router.get("/unread")
def get_unread_alerts(user: dict = Depends(get_current_user)):
    """
    Retrieves all unread alerts for the logged-in user.
    
    - user: Authenticated user from JWT
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM alerts WHERE user_id = %s AND is_read = FALSE", 
                   (user["user_id"],))
    alerts = cursor.fetchall()

    return {"alerts": alerts}
#📂 Step 5: Mark an Alert as Read (/alerts/mark_as_read)
#✅ How it works?
#1️⃣ Ensures the alert belongs to the user before updating.
#2️⃣ Marks the alert as read (is_read = TRUE).
#3️⃣ Returns a success message once updated.
@router.put("/mark_as_read/{alert_id}")
def mark_alert_as_read(alert_id: int, user: dict = Depends(get_current_user)):
    """
    Marks a specific alert as read.
    
    - alert_id: ID of the alert to update
    - user: Authenticated user from JWT
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure the alert belongs to the user
    cursor.execute("SELECT * FROM alerts WHERE alert_id = %s AND user_id = %s", 
                   (alert_id, user["user_id"]))
    alert = cursor.fetchone()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found or unauthorized access")

    cursor.execute("UPDATE alerts SET is_read = TRUE WHERE alert_id = %s", (alert_id,))
    conn.commit()

    return {"message": "Alert marked as read"}
#📂 Step 6: Delete All Read Alerts (/alerts/delete_read)
#✅ How it works?
#1️⃣ Deletes only read alerts (prevents deleting unread ones).
#2️⃣ Ensures alerts belong to the user.
#3️⃣ Prevents clutter by removing old notifications.
