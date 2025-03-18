# 🔐 Login & Signup UI: Manages user authentication UI
# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # Handles API calls to backend
from config import API_URL  # Backend URL configuration
from app import BudgetBuddyApp  # Main application UI

# =============================
# 📌 Login Window Class
# =============================
class LoginWindow:
    def __init__(self, root):
        """
        Initializes the login window.

        - root: Tkinter root window
        """
        self.root = root
        self.root.title("Login - Budget Buddy")
        self.root.geometry("400x300")

        self.create_login_screen()

    # =============================
    # 📌 Create Login Screen
    # =============================
    def create_login_screen(self):
        """
        Displays the login UI for users.
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
            token = data["access_token"]
            self.get_user_role(token)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password")

    # =============================
    # 📌 Get User Role (Client or Banker)
    # =============================
    def get_user_role(self, token):
        """
        Retrieves the role of the authenticated user.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/auth/profile", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            role = user_data["role"]
            self.open_dashboard(token, role)
        else:
            messagebox.showerror("Error", "Failed to retrieve user data")

    # =============================
    # 📌 Open Dashboard Based on Role
    # =============================
    def open_dashboard(self, token, role):
        """
        Opens the correct dashboard based on user role.

        - token: JWT authentication token
        - role: "client" or "banker"
        """
        self.clear_window()
        if role == "client":
            BudgetBuddyApp(self.root, token)  # Open client dashboard
        elif role == "banker":
            from banker_dashboard import BankerDashboard  # Import dynamically to avoid circular import
            BankerDashboard(self.root, token)  # Open banker dashboard

    # =============================
    # 📌 Create Registration Screen
    # =============================
    def create_register_screen(self):
        """
        Displays the registration UI.
        """
        self.clear_window()
        tk.Label(self.root, text="Register", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Name:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Label(self.root, text="Role (client/banker):").pack()
        self.role_entry = tk.Entry(self.root)
        self.role_entry.pack()

        ttk.Button(self.root, text="Register", command=self.register).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_login_screen).pack()

    # =============================
    # 📌 Register Functionality
    # =============================
    def register(self):
        """
        Registers a new user.
        """
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = self.role_entry.get().lower()

        if role not in ["client", "banker"]:
            messagebox.showerror("Error", "Role must be 'client' or 'banker'")
            return

        response = requests.post(f"{API_URL}/auth/register", json={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        })

        if response.status_code == 200:
            messagebox.showinfo("Success", "Account registered! Please log in.")
            self.create_login_screen()
        else:
            messagebox.showerror("Error", "Failed to register. Email may already be in use.")

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
    LoginWindow(root)
    root.mainloop()
