#!/usr/bin/env python3
"""
Budget Buddy - Flask Backend
This script provides the backend API for the Budget Buddy application using Flask.
"""

import logging
import mysql.connector
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    filename="backend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)

# JWT configuration
SECRET_KEY = "your-secret-key"  # Replace with a secure key in production
TOKEN_EXPIRY = 3600  # Token expiry time in seconds (1 hour)

# Database class
class Database:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'budget_buddy'
        }
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("Successfully connected to the database")
            self.ensure_database_schema()
        except mysql.connector.Error as err:
            logger.error(f"Failed to connect to database: {str(err)}")
            raise SystemExit("Database connection failed. Check backend.log for details.")

    def ensure_database_schema(self):
        """Ensure the database schema is set up correctly"""
        # Create users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                user_type ENUM('client', 'banker', 'admin') NOT NULL DEFAULT 'client',
                balance DECIMAL(10,2) DEFAULT 0.00,
                banker_id INT,
                FOREIGN KEY (banker_id) REFERENCES users(user_id)
            )
        """)

        # Create categories table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            )
        """)

        # Insert default categories
        default_categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Other']
        for category in default_categories:
            self.cursor.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (category,))

        self.conn.commit()

    def get_connection(self):
        return self.conn

# Initialize database
db = Database()
db_conn = db.get_connection()

def verify_token():
    """Verify JWT token from Authorization header"""
    token = request.headers.get('Authorization')
    if not token:
        return None, jsonify({"success": False, "message": "Token is missing!"}), 401

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({"success": False, "message": "Token has expired!"}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({"success": False, "message": "Invalid token!"}), 401

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    user_type = data.get('user_type', 'client')

    # Validate required fields
    if not name:
        return jsonify({"success": False, "message": "Name is required!"}), 400
    if not email:
        return jsonify({"success": False, "message": "Email is required!"}), 400
    if not password:
        return jsonify({"success": False, "message": "Password is required!"}), 400
    if user_type not in ['client', 'banker', 'admin']:
        return jsonify({"success": False, "message": "Invalid user type!"}), 400

    # Validate password (minimum 8 characters)
    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters long!"}), 400

    # Check if email already exists
    cursor = db_conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"success": False, "message": "Email already exists!"}), 400

    # Hash password and insert user
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, user_type)
        )
        db_conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        logger.info(f"User registered: user_id={user_id}, email={email}")
        return jsonify({"success": True, "message": "User created successfully!", "user_id": user_id}), 200
    except mysql.connector.Error as err:
        logger.error(f"Database error during registration: {str(err)}")
        return jsonify({"success": False, "message": "Database error during registration."}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required!"}), 400

    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        cursor.close()
        return jsonify({"success": False, "message": "Invalid email or password!"}), 401

    token = jwt.encode({
        'user_id': user['user_id'],
        'email': user['email'],
        'user_type': user['user_type'],
        'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY)
    }, SECRET_KEY, algorithm="HS256")

    cursor.close()
    logger.info(f"User logged in: user_id={user['user_id']}, email={email}")
    return jsonify({
        "success": True,
        "token": token,
        "user_id": user['user_id'],
        "name": user['name'],
        "email": user['email'],
        "user_type": user['user_type'],
        "balance": float(user['balance']) if user['balance'] is not None else 0.0,
        "banker_id": user['banker_id']
    }), 200

@auth_bp.route('/clients', methods=['GET'])
def get_clients():
    data, error = verify_token()
    if error:
        return error

    if data['user_type'] not in ['banker', 'admin']:
        return jsonify({"success": False, "message": "Unauthorized access!"}), 403

    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, balance FROM users WHERE user_type = 'client'")
    clients = cursor.fetchall()
    cursor.close()

    for client in clients:
        client['balance'] = float(client['balance']) if client['balance'] is not None else 0.0

    return jsonify({"success": True, "clients": clients}), 200

@auth_bp.route('/update_balance', methods=['POST'])
def update_balance():
    data, error = verify_token()
    if error:
        return error

    if data['user_type'] not in ['banker', 'admin']:
        return jsonify({"success": False, "message": "Unauthorized access!"}), 403

    request_data = request.get_json()
    user_id = request_data.get('user_id')
    amount = request_data.get('amount')

    if not user_id or amount is None:
        return jsonify({"success": False, "message": "User ID and amount are required!"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be positive!"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount!"}), 400

    cursor = db_conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({"success": False, "message": "User not found!"}), 404

        db_conn.commit()
        cursor.close()
        logger.info(f"Balance updated: user_id={user_id}, amount={amount}")
        return jsonify({"success": True, "message": "Balance updated successfully!"}), 200
    except mysql.connector.Error as err:
        logger.error(f"Database error during balance update: {str(err)}")
        return jsonify({"success": False, "message": "Database error during balance update."}), 500

# Register the blueprint
app.register_blueprint(auth_bp, url_prefix='/api')

if __name__ == "__main__":
    logger.info("Starting Flask backend server...")
    app.run(host='127.0.0.1', port=5000, debug=False)