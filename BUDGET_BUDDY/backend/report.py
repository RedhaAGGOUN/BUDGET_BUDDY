#This module generates financial reports based on user transactions.
# Import necessary libraries
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from auth import get_current_user

# Initialize API router
router = APIRouter(prefix="/reports", tags=["Reports"])

# =============================
# 📌 Get Monthly Spending Report
# =============================
@router.get("/monthly_spending")
def get_monthly_spending(year: int, month: int, user: dict = Depends(get_current_user)):
    """
    Generates a spending report for a specific month.

    - year: Year of the report (e.g., 2024)
    - month: Month of the report (e.g., 3 for March)
    - user: Must own the accounts being analyzed
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch total expenses for the given month
    cursor.execute("""
        SELECT SUM(amount) as total_spent 
        FROM transactions 
        WHERE account_id IN (SELECT account_id FROM accounts WHERE user_id = %s)
        AND transaction_type = 'withdrawal'
        AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
    """, (user["user_id"], year, month))

    result = cursor.fetchone()
    total_spent = result["total_spent"] if result["total_spent"] else 0.00

    return {"year": year, "month": month, "total_spent": total_spent}

# =============================
# 📌 Get Yearly Spending Report
# =============================
@router.get("/yearly_spending")
def get_yearly_spending(year: int, user: dict = Depends(get_current_user)):
    """
    Generates a spending report for a full year.

    - year: Year of the report (e.g., 2024)
    - user: Must own the accounts being analyzed
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch total expenses for the year
    cursor.execute("""
        SELECT MONTH(transaction_date) as month, SUM(amount) as total_spent
        FROM transactions 
        WHERE account_id IN (SELECT account_id FROM accounts WHERE user_id = %s)
        AND transaction_type = 'withdrawal'
        AND YEAR(transaction_date) = %s
        GROUP BY MONTH(transaction_date)
    """, (user["user_id"], year))

    results = cursor.fetchall()
    return {"year": year, "monthly_spending": results}

# =============================
# 📌 Get Category-Based Spending Report
# =============================
@router.get("/category_spending")
def get_category_spending(year: int, month: int, user: dict = Depends(get_current_user)):
    """
    Generates a category-based expense report for a given month.

    - year: Year of the report (e.g., 2024)
    - month: Month of the report (e.g., 3 for March)
    - user: Must own the accounts being analyzed
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch total expenses grouped by category
    cursor.execute("""
        SELECT category, SUM(amount) as total_spent
        FROM transactions 
        WHERE account_id IN (SELECT account_id FROM accounts WHERE user_id = %s)
        AND transaction_type = 'withdrawal'
        AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
        GROUP BY category
    """, (user["user_id"], year, month))

    results = cursor.fetchall()
    return {"year": year, "month": month, "category_spending": results}

# =============================
# 📌 Get Cash Flow Report (Income vs Expenses)
# =============================
@router.get("/cash_flow")
def get_cash_flow(year: int, month: int, user: dict = Depends(get_current_user)):
    """
    Generates a cash flow report (Income vs Expenses).

    - year: Year of the report (e.g., 2024)
    - month: Month of the report (e.g., 3 for March)
    - user: Must own the accounts being analyzed
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch total deposits (income)
    cursor.execute("""
        SELECT SUM(amount) as total_income
        FROM transactions 
        WHERE account_id IN (SELECT account_id FROM accounts WHERE user_id = %s)
        AND transaction_type = 'deposit'
        AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
    """, (user["user_id"], year, month))
    income_result = cursor.fetchone()
    total_income = income_result["total_income"] if income_result["total_income"] else 0.00

    # ✅ Fetch total withdrawals (expenses)
    cursor.execute("""
        SELECT SUM(amount) as total_expenses
        FROM transactions 
        WHERE account_id IN (SELECT account_id FROM accounts WHERE user_id = %s)
        AND transaction_type = 'withdrawal'
        AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
    """, (user["user_id"], year, month))
    expense_result = cursor.fetchone()
    total_expenses = expense_result["total_expenses"] if expense_result["total_expenses"] else 0.00

    net_cash_flow = total_income - total_expenses

    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cash_flow": net_cash_flow
    }
