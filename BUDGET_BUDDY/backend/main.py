# 🚀Starts FastAPI server, loads routes
# Import necessary libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API route modules
from auth import router as auth_router
from accounts import router as accounts_router
from transactions import router as transactions_router
from alerts import router as alerts_router
from banker import router as banker_router

# =============================
# 📌 Initialize FastAPI App
# =============================
app = FastAPI(
    title="Budget Buddy API",  # API Title (visible in Swagger UI)
    description="An API for managing personal finance with banking features.",
    version="1.0.0"
)

# =============================
# 📌 Enable CORS for Frontend
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔴 Set this to specific domains in production for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

# =============================
# 📌 Register API Routes
# =============================
app.include_router(auth_router, prefix="/auth")  # 🔐 Authentication endpoints
app.include_router(accounts_router, prefix="/accounts")  # 🏦 Account management
app.include_router(transactions_router, prefix="/transactions")  # 💰 Transactions
app.include_router(alerts_router, prefix="/alerts")  # 🔔 Notifications & alerts
app.include_router(banker_router, prefix="/banker")  # 👨‍💼 Banker functionalities

# =============================
# 📌 Root Endpoint (API Info)
# =============================
@app.get("/")
def home():
    """
    Root endpoint that provides API information.
    """
    return {
        "message": "Welcome to Budget Buddy API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# =============================
# 📌 Run the Server (For Debugging)
# =============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # 🔥 Starts the FastAPI server

