# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # Handles API calls to backend
from config import API_URL  # Backend URL configuration
from transactions_ui import TransactionsUI
from reports_ui import ReportsUI
from banker_dashboard import BankerDashboard

# =============================
# 📌 Dashboard Class (Client & Banker)
# =============================
class Dashboard:
    def __init__(self, root, token, role):
        """
        Initializes the main dashboard for users.

        - root: Tkinter root window
        - token: JWT authentication token
        - role: "client" or "banker"
        """
        self.root = root
        self.root.title("Dashboard - Budget Buddy")
        self.root.geometry("600x400")

        self.token = token  # Store authentication token
        self.role = role  # Store user role

        self.create_dashboard()

    # =============================
    # 📌 Create Dashboard UI
    # =============================
    def create_dashboard(self):
        """
        Displays the main dashboard options based on user role.
        """
        self.clear_window()
        tk.Label(self.root, text="Welcome to Budget Buddy", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.root, text="View Accounts", command=self.view_accounts).pack(pady=5)
        ttk.Button(self.root, text="Manage Transactions", command=lambda: TransactionsUI(self.root, self.token)).pack(pady=5)
        ttk.Button(self.root, text="View Reports", command=lambda: ReportsUI(self.root, self.token)).pack(pady=5)
        ttk.Button(self.root, text="View Alerts", command=self.view_alerts).pack(pady=5)

        if self.role == "banker":
            ttk.Button(self.root, text="Manage Clients", command=lambda: BankerDashboard(self.root, self.token)).pack(pady=5)

        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=10)

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
    # 📌 View Alerts & Notifications
    # =============================
    def view_alerts(self):
        """
        Fetches and displays user alerts.
        """
        self.clear_window()
        tk.Label(self.root, text="Notifications", font=("Arial", 16)).pack(pady=10)

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/alerts/unread", headers=headers)

        if response.status_code == 200:
            alerts = response.json()["alerts"]
            for alert in alerts:
                ttk.Label(self.root, text=f"{alert['message']}").pack()

            ttk.Button(self.root, text="Mark All as Read", command=self.mark_alerts_as_read).pack(pady=5)
        else:
            messagebox.showerror("Error", "Failed to retrieve alerts")

        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack(pady=10)

    def mark_alerts_as_read(self):
        """
        Marks all alerts as read.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.put(f"{API_URL}/alerts/mark_as_read/0", headers=headers)  # `0` marks all as read

        if response.status_code == 200:
            messagebox.showinfo("Success", "All alerts marked as read")
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Failed to mark alerts as read")

    # =============================
    # 📌 Logout Functionality
    # =============================
    def logout(self):
        """
        Logs out the user and returns to the login screen.
        """
        self.token = None
        self.clear_window()
        from login import LoginWindow  # Import dynamically to avoid circular import
        LoginWindow(self.root)

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
# 📌 Run the Dashboard for Testing
# =============================
if __name__ == "__main__":
    root = tk.Tk()
    fake_token = "sample_token"  # Replace with actual token after login
    fake_role = "client"  # Change to "banker" for banker dashboard
    Dashboard(root, fake_token, fake_role)
    root.mainloop()
