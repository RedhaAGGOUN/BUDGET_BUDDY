# 🗄️Database Connection Manages MySQL connection, executes queries
# Import necessary libraries
import mysql.connector  # MySQL database connector
from mysql.connector import Error
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME  # Import database credentials from config.py

# ===================================
# 📌 Function: Get Database Connection
# ===================================
def get_db_connection():
    """
    Establishes and returns a database connection.
    
    ✅ Uses MySQL database credentials from config.py
    ✅ Handles connection errors gracefully
    ✅ Must be called before executing any SQL queries
    """
    try:
        # ✅ Establish connection with MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,        # Database server (e.g., localhost)
            user=DB_USER,        # MySQL username (e.g., root)
            password=DB_PASSWORD,  # MySQL password
            database=DB_NAME     # Database name
        )
        if conn.is_connected():
            print("✅ Database connection established successfully.")
            return conn
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None  # Return None if connection fails

# =====================================
# 📌 Function: Execute SQL Query (Insert, Update, Delete)
# =====================================
def execute_query(query: str, params: tuple = ()):
    """
    Executes a SQL query that modifies data (INSERT, UPDATE, DELETE).
    
    ✅ Ensures connection is established before execution
    ✅ Uses prepared statements to prevent SQL injection
    ✅ Closes connection after execution to prevent leaks
    """
    conn = get_db_connection()
    if conn is None:
        raise Exception("❌ Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute(query, params)  # Execute query with parameters
        conn.commit()  # ✅ Save changes to database
        print(f"✅ Query executed successfully: {query}")
    except Error as e:
        conn.rollback()  # ❌ Rollback if error occurs
        print(f"❌ Query execution error: {e}")
    finally:
        cursor.close()
        conn.close()  # ✅ Always close connection to prevent leaks

# =====================================
# 📌 Function: Fetch Data (SELECT Queries)
# =====================================
def fetch_query(query: str, params: tuple = ()):
    """
    Executes a SELECT query and fetches the results.
    
    ✅ Ensures connection is established before execution
    ✅ Uses prepared statements to prevent SQL injection
    ✅ Fetches all results and returns them
    ✅ Closes connection after execution to prevent leaks
    """
    conn = get_db_connection()
    if conn is None:
        raise Exception("❌ Database connection failed")

    cursor = conn.cursor(dictionary=True)  # ✅ Fetch results as dictionary
    try:
        cursor.execute(query, params)  # Execute query
        results = cursor.fetchall()  # Fetch all results
        print(f"✅ Data fetched successfully: {query}")
        return results
    except Error as e:
        print(f"❌ Query execution error: {e}")
        return None  # Return None if error occurs
    finally:
        cursor.close()
        conn.close()  # ✅ Always close connection to prevent leaks

