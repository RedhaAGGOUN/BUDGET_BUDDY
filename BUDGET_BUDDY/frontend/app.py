# 🖥️ UI Application: Runs the main UI for users & bankers
# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # Handles API calls to the backend
from config import API_URL  # Backend URL configuration

# =============================
# 📌 Initialize Main Application
# =============================
class BudgetBuddyApp:
    def __init__(self, root):
        """
        Initializes the main application window.
        
        - root: Tkinter root window
        """
        self.root = root
        self.root.title("Budget Buddy - Personal Finance Manager")
        self.root.geometry("600x400")

        self.token = None  # Stores authentication token after login
        self.user_role = None  # Stores whether the user is a client or banker
        
        self.create_login_screen()

    # =============================
    # 📌 Create Login Screen
    # =============================
    def create_login_screen(self):
        """
        Displays the login screen for users.
        """
        self.clear_window()
        tk.Label(self.root, text="Login", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        ttk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        ttk.Button(self.root, text="Register", command=self.create_register_screen).pack()

    # =============================
    # 📌 Login Functionality
    # =============================
    def login(self):
        """
        Authenticates user and retrieves an access token.
        """
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        response = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.get_user_role()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password")

    # =============================
    # 📌 Get User Role (Client or Banker)
    # =============================
    def get_user_role(self):
        """
        Retrieves the role of the logged-in user.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/auth/profile", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            self.user_role = user_data["role"]
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Failed to retrieve user data")

    # =============================
    # 📌 Create User Dashboard
    # =============================
    def create_dashboard(self):
        """
        Displays the main dashboard based on user role.
        """
        self.clear_window()
        tk.Label(self.root, text="Dashboard", font=("Arial", 16)).pack(pady=10)

        if self.user_role == "client":
            ttk.Button(self.root, text="View Accounts", command=self.view_accounts).pack(pady=5)
            ttk.Button(self.root, text="Transactions", command=self.view_transactions).pack(pady=5)
            ttk.Button(self.root, text="Reports", command=self.view_reports).pack(pady=5)
        elif self.user_role == "banker":
            ttk.Button(self.root, text="Manage Clients", command=self.view_clients).pack(pady=5)
            ttk.Button(self.root, text="Perform Transactions", command=self.perform_transaction).pack(pady=5)

        ttk.Button(self.root, text="Logout", command=self.create_login_screen).pack(pady=5)

    # =============================
    # 📌 View User Accounts
    # =============================
    def view_accounts(self):
        """
        Fetches and displays user accounts.
        """
        self.clear_window()
        tk.Label(self.root, text="Your Accounts", font=("Arial", 16)).pack(pady=10)

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/accounts/list", headers=headers)

        if response.status_code == 200:
            accounts = response.json()["accounts"]
            for acc in accounts:
                ttk.Label(self.root, text=f"{acc['account_type'].capitalize()} - ${acc['balance']}").pack()
        else:
            messagebox.showerror("Error", "Failed to retrieve accounts")

        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack(pady=10)

    # =============================
    # 📌 View Transactions
    # =============================
    def view_transactions(self):
        """
        Fetches and displays user transaction history.
        """
        self.clear_window()
        tk.Label(self.root, text="Transaction History", font=("Arial", 16)).pack(pady=10)

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/transactions/history?account_id=1", headers=headers)

        if response.status_code == 200:
            transactions = response.json()["transactions"]
            for txn in transactions:
                ttk.Label(self.root, text=f"{txn['transaction_type']} - ${txn['amount']} - {txn['category']}").pack()
        else:
            messagebox.showerror("Error", "Failed to retrieve transactions")

        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack(pady=10)

    # =============================
    # 📌 View Reports
    # =============================
    def view_reports(self):
        """
        Fetches and displays financial reports.
        """
        self.clear_window()
        tk.Label(self.root, text="Reports", font=("Arial", 16)).pack(pady=10)

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/reports/monthly_spending?year=2024&month=3", headers=headers)

        if response.status_code == 200:
            report = response.json()
            ttk.Label(self.root, text=f"Total Spent: ${report['total_spent']}").pack()
        else:
            messagebox.showerror("Error", "Failed to retrieve reports")

        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack(pady=10)

    # =============================
    # 📌 Clear Window
    # =============================
    def clear_window(self):
        """
        Clears all elements from the window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

# =============================
# 📌 Run the Application
# =============================
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetBuddyApp(root)
    root.mainloop()
