# 📊 Models & Schema Defines ORM models for tables (users, transactions, etc.)
# Import necessary libraries
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Enum, Boolean, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
from database import get_db_connection

# Initialize the ORM base
Base = declarative_base()

# =============================
# 📌 User Model (Clients & Bankers)
# =============================
class User(Base):
    """
    Represents a user in the system (Client or Banker).
    
    - Stores hashed passwords for security
    - Role determines access level ("client" or "banker")
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("client", "banker"), default="client")
    created_at = Column(DateTime, default=func.now())

    # Relationship: One user can have multiple accounts
    accounts = relationship("Account", back_populates="user")

# =============================
# 📌 Account Model
# =============================
class Account(Base):
    """
    Represents a bank account.
    
    - Linked to a specific user (client)
    - Has a balance and account type
    """
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    balance = Column(DECIMAL(12,2), default=0.00)
    account_type = Column(Enum("checking", "savings"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship: An account belongs to a user
    user = relationship("User", back_populates="accounts")

# =============================
# 📌 Transaction Model
# =============================
class Transaction(Base):
    """
    Represents a financial transaction.
    
    - Linked to an account
    - Can be a deposit, withdrawal, or transfer
    """
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    amount = Column(DECIMAL(12,2), nullable=False)
    transaction_type = Column(Enum("deposit", "withdrawal", "transfer"), nullable=False)
    category = Column(String(50), default="Other")
    description = Column(String(255))
    transaction_date = Column(DateTime, default=func.now())

    # Relationship: A transaction is linked to an account
    account = relationship("Account")

# =============================
# 📌 Banker-Client Relationship Model
# =============================
class BankerClient(Base):
    """
    Represents the relationship between a banker and their clients.
    
    - Each banker can manage multiple clients
    - Each client can have multiple bankers (optional)
    """
    __tablename__ = "banker_clients"

    banker_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    client_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

# =============================
# 📌 Alerts Model
# =============================
class Alert(Base):
    """
    Represents an alert or notification for a user.
    
    - Can be used for overdraft warnings or security alerts
    """
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship: An alert is linked to a user
    user = relationship("User")

# =============================
# 📌 Database Initialization Function
# =============================
def init_db():
    """
    Creates all tables in the database if they do not exist.
    """
    conn = get_db_connection()
    Base.metadata.create_all(bind=conn)

if __name__ == "__main__":
    init_db()  # Run this script once to create tables
