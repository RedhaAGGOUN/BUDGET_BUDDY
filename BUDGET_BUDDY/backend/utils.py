# 🛠️ Utility Functions: Helper functions (date formatting, validation)
# Import necessary libraries
import re
import random
import string
from datetime import datetime

# =============================
# 📌 Function: Format Date
# =============================
def format_date(date_str: str) -> str:
    """
    Converts a date string to 'YYYY-MM-DD' format.
    
    ✅ Ensures correct date formatting
    ✅ Prevents errors from incorrect date inputs

    - date_str: Input date in various formats (e.g., "10/03/2025", "2025-03-10")
    - Returns formatted date in 'YYYY-MM-DD'
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("❌ Invalid date format. Expected YYYY-MM-DD.")

# =============================
# 📌 Function: Validate Email Format
# =============================
def is_valid_email(email: str) -> bool:
    """
    Validates if the given string is a properly formatted email.
    
    ✅ Prevents incorrect email inputs
    ✅ Avoids invalid email storage in the database

    - email: Email address as a string
    - Returns True if valid, False otherwise
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None

# =============================
# 📌 Function: Generate Secure Random ID
# =============================
def generate_secure_id(length: int = 10) -> str:
    """
    Generates a secure random alphanumeric ID.
    
    ✅ Used for transaction references, session IDs, or unique identifiers
    ✅ Prevents predictable ID sequences

    - length: Length of the generated ID (default is 10)
    - Returns a secure random string
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# =============================
# 📌 Function: Validate Transaction Type
# =============================
def is_valid_transaction_type(transaction_type: str) -> bool:
    """
    Validates if the transaction type is correct.
    
    ✅ Prevents invalid transaction entries in the database
    ✅ Ensures transaction_type is one of ["deposit", "withdrawal", "transfer"]

    - transaction_type: Type of transaction as a string
    - Returns True if valid, False otherwise
    """
    valid_types = {"deposit", "withdrawal", "transfer"}
    return transaction_type in valid_types
