#!/usr/bin/env python3

"""

Budget Buddy - Database Module

This module handles database connections and queries for the Budget Buddy application.

"""

import mysql.connector
import bcrypt
import logging
from mysql.connector import pooling, Error  # Import Error specifically
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.connection_pool = None
        self.initialize_pool()

    def initialize_pool(self):
        """Initialize the connection pool using environment variables."""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="budget_buddy_pool",
                pool_size=int(os.getenv('DB_POOL_SIZE', 5)),  # Default to 5, use .env
                host=os.getenv('DB_HOST', 'localhost'),  # Default to localhost
                user=os.getenv('DB_USER', 'root'),  # Default to root, use .env
                password=os.getenv('DB_PASSWORD'),  # No default, MUST be in .env
                database=os.getenv('DB_NAME', 'budget_buddy'),  # Default, use .env
                port=int(os.getenv('DB_PORT', 3306)),  # Default MySQL port
                # Enable auto-reconnect with exponential backoff
                use_pure=True, # Required for reconnect
                connect_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10)), # seconds, default 10
                # Removed: connection_timeout=30,  # This is deprecated, use connect_timeout
            )
            logger.info("Database connection pool initialized successfully")
        except Error as e:  # Use the specific Error class
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool, with retry logic."""
        max_retries = int(os.getenv('DB_GET_CONNECTION_RETRIES', 3)) # default 3 retries
        retry_delay = int(os.getenv('DB_RETRY_DELAY', 1)) # seconds, default 1

        for attempt in range(max_retries):
            try:
                return self.connection_pool.get_connection()
            except Error as e:
                logger.error(f"Failed to get database connection (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)  # Wait before retrying
                    retry_delay *= 2 # Exponential backoff
                else:
                    raise  # Re-raise the exception after all retries

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Execute a SQL query and return results, with retry logic."""
        connection = None
        cursor = None
        max_retries = int(os.getenv('DB_EXECUTE_QUERY_RETRIES', 3)) # default 3 retries
        retry_delay = int(os.getenv('DB_RETRY_DELAY', 1)) # seconds, default 1

        for attempt in range(max_retries):
            try:
                connection = self.get_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())

                if commit:
                    connection.commit()
                    return cursor.rowcount
                elif fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return None
            except Error as e:
                logger.error(f"Database query failed (attempt {attempt + 1}/{max_retries}): {e}")
                if commit and connection:
                    connection.rollback()
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                else:
                    raise  # Re-raise after all retries
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()  # Return connection to the pool


    def hash_password(self, password):
        """Hash a password using bcrypt"""
        try:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            return None  # Important: Return None on failure

    def check_password(self, password, hashed_password):
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to check password: {e}")
            return False  # Important: Return False on failure


if __name__ == "__main__":
    # Test the database connection
    db = Database()
    try:
        result = db.execute_query("SELECT 1", fetch_one=True)
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")

