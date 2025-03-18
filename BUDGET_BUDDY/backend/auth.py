# 🔑 Authentication Handles user login, registration, password hashing (bcrypt), JWT tokens
#📌 backend/auth.py - Complete Code with Explanations
#This module handles authentication (registration, login, and JWT-based security) for Budget Buddy.
#✅ User Registration (hashed passwords with bcrypt)
#✅ User Login (JWT authentication)
#✅ Token-based authentication for protected routes
#📂 Step 1: Import Dependencies
#✅ Why?
#APIRouter creates modular API routes for authentication.
#bcrypt hashes and verifies passwords securely.
#jwt handles authentication tokens.
#datetime sets token expiration times.
#database.get_db_connection() interacts with MySQL.
#config.py centralizes security settings (SECRET_KEY, ALGORITHM, etc.).
from fastapi import APIRouter, HTTPException, Depends
from passlib.hash import bcrypt
import jwt
import datetime
from database import get_db_connection
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
#📂 Step 2: Define API Router
#✅ Why?
#prefix="/auth" groups authentication endpoints under /auth/....
#tags=["Authentication"] improves API documentation (/docs).
router = APIRouter(prefix="/auth", tags=["Authentication"])

#📂 Step 3: Hash Passwords with bcrypt
#✅ Why?
#Ensures passwords are never stored in plain text.
#bcrypt automatically adds a salt (prevents rainbow table attacks).
def hash_password(password: str) -> str:
    """
    Hashes the given password using bcrypt.
    """
    return bcrypt.hash(password)

#📂 Step 4: Verify Passwords
#✅ Why?
#Ensures correct password validation at login.
#Uses bcrypt’s built-in verification method for security.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the given password matches the stored hash.
    """
    return bcrypt.verify(plain_password, hashed_password)
#Step 5: Generate JWT Tokens
#✅ Why?
#JWT includes an expiration time (prevents unlimited access).
#Uses SECRET_KEY and ALGORITHM for security.
#Allows user authentication without storing session data.
def create_access_token(data: dict):
    """
    Generates a JWT access token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#Step 6: User Registration (/auth/register)
#✅ How it works?
#1️⃣ Hashes the password before storing it.
#2️⃣ Ensures email is unique (catches duplicate entry errors).
#3️⃣ Stores user details securely in MySQL.
#4️⃣ Returns a success message upon registration.
@router.post("/register")
def register_user(name: str, email: str, password: str):
    """
    Registers a new user with a hashed password.
    
    - name: Full name of the user
    - email: Unique email address
    - password: Securely hashed before storing
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                       (name, email, hashed_password))
        conn.commit()
        return {"message": "User registered successfully"}
    except:
        raise HTTPException(status_code=400, detail="Email already registered")
#Step 7: User Login (/auth/login)
#✅ How it works?
#1️⃣ Fetches user data from MySQL by email.
#2️⃣ Verifies the entered password against the hashed password.
#3️⃣ Generates a JWT token upon successful authentication.
#4️⃣ Returns the access token to the user.
@router.post("/login")
def login_user(email: str, password: str):
    """
    Authenticates a user and returns a JWT token.
    
    - email: Registered email address
    - password: Raw password (verified against hashed password)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user["user_id"]})
    return {"access_token": token}
#📂 Step 8: Protect Routes (get_current_user)
#✅ How it works?
#1️⃣ Decodes the JWT token and extracts the user_id.
#2️⃣ Handles expired tokens (prevents unlimited access).
#3️⃣ Returns authenticated user data for protected routes.
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extracts user information from the JWT token.
    
    - token: JWT access token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
#📂 Step 9: Secure an Example API Route
#✅ Why?
#Requires JWT authentication to access user data.
#Returns the user's profile information securely.
