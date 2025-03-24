#!/usr/bin/env python3

"""

Budget Buddy - Tkinter Frontend

This script provides the frontend GUI for the Budget Buddy application using Tkinter.

"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="frontend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "http://127.0.0.1:5000"  # Removed /api to match backend routes


class BudgetBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Buddy")
        self.style = ttkb.Style(theme="flatly")
        self.root.geometry("1000x700")  # Increased size for better layout

        self.token = None
        self.user_id = None
        self.user_type = None
        self.name = None
        self.email = None
        self.balance = 0.0
        self.banker_id = None

        # Variables for login/register forms
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.user_type_var = tk.StringVar(value="client")

        # Variables for transaction form
        self.transaction_type_var = tk.StringVar(value="deposit")
        self.transaction_amount_var = tk.StringVar()
        self.transaction_category_var = tk.StringVar()
        self.transaction_recipient_email_var = tk.StringVar()  # For transfers
        self.transaction_description_var = tk.StringVar() # Added description

        # Variables for date filters
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        # Client ID for banker/admin actions
        self.client_id_var = tk.StringVar()
        self.deposit_amount_var = tk.StringVar()

        self.show_login_screen()


    def clear_screen(self):
        """Clear all widgets from the screen"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def validate_password(self, password):
        """Validate password requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long!"
        return True, ""

    def show_login_screen(self):
        """Display the login screen"""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttkb.Label(frame, text="Budget Buddy Login", font=("Helvetica", 20, "bold")).pack(pady=20)

        ttkb.Label(frame, text="Email").pack()
        ttkb.Entry(frame, textvariable=self.email_var).pack(pady=5)

        ttkb.Label(frame, text="Password").pack()
        ttkb.Entry(frame, textvariable=self.password_var, show="*").pack(pady=5)

        ttkb.Button(frame, text="Login", command=self.login, bootstyle="primary").pack(pady=10)
        ttkb.Button(frame, text="Register", command=self.show_register_screen, bootstyle="success").pack(pady=5)


    def show_register_screen(self):
        """Display the registration screen"""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttkb.Label(frame, text="Budget Buddy Registration", font=("Helvetica", 20, "bold")).pack(pady=20)

        ttkb.Label(frame, text="Name").pack()
        ttkb.Entry(frame, textvariable=self.name_var).pack(pady=5)

        ttkb.Label(frame, text="Email").pack()
        ttkb.Entry(frame, textvariable=self.email_var).pack(pady=5)

        ttkb.Label(frame, text="Password").pack()
        ttkb.Entry(frame, textvariable=self.password_var, show="*").pack(pady=5)

        ttkb.Label(frame, text="User Type").pack()
        user_type_combo = ttkb.Combobox(frame, textvariable=self.user_type_var, values=["client", "banker", "admin"], state="readonly")
        user_type_combo.pack(pady=5)
        # Bind the selection event to clear banker_id if user_type changes
        user_type_combo.bind("<<ComboboxSelected>>", lambda event: self.clear_banker_id_if_not_client())


        ttkb.Button(frame, text="Register", command=self.register, bootstyle="primary").pack(pady=10)
        ttkb.Button(frame, text="Back to Login", command=self.show_login_screen, bootstyle="secondary").pack(pady=5)

    def clear_banker_id_if_not_client(self):
        """Clears banker_id if user_type is not client"""
        if self.user_type_var.get() != 'client':
            self.banker_id = None

    def login(self):
        """Login user"""
        email = self.email_var.get().strip()
        password = self.password_var.get()

        if not email or not password:
            messagebox.showerror("Login Error", "Please fill in all fields")
            logger.warning("Login failed: Missing fields")
            return

        try:
            logger.info(f"Sending login request for email: {email}")
            response = requests.post(
                f"{API_URL}/login",
                json={"email": email, "password": password},
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                self.token = data["token"]
                self.user_id = data["user_id"]
                self.name = data["name"]
                self.email = data["email"]
                self.user_type = data["user_type"]
                self.balance = data["balance"]
                self.banker_id = data.get("banker_id")  # Use .get() to handle potential missing key
                logger.info(f"Login successful: user_id={self.user_id}, email={email}")
                self.show_main_screen()
            else:
                messagebox.showerror("Login Error", data["message"])
                logger.warning(f"Login failed: {data['message']}")
        except requests.RequestException as e:
            messagebox.showerror("Login Error", "Failed to connect to the server")
            logger.error(f"Login request failed: {str(e)}")

    def register(self):
        """Register a new user"""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        user_type = self.user_type_var.get()

        if not all([name, email, password]):
            messagebox.showerror("Registration Error", "Please fill in all fields")
            logger.warning("Registration failed: Missing fields")
            return

        # Validate password
        is_valid, message = self.validate_password(password)
        if not is_valid:
            messagebox.showerror("Registration Error", message)
            logger.warning(f"Registration failed: {message}")
            return

        try:
            logger.info(f"Sending registration request for email: {email}")
            response = requests.post(
                f"{API_URL}/register",
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "user_type": user_type
                },
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                messagebox.showinfo("Registration Success", "User registered successfully! Please login.")
                logger.info(f"Registration successful: user_id={data['user_id']}, email={email}")
                self.show_login_screen()
            else:
                messagebox.showerror("Registration Error", data["message"])
                logger.warning(f"Registration failed: {data['message']}")
        except requests.RequestException as e:
            messagebox.showerror("Registration Error", "Failed to connect to the server")
            logger.error(f"Registration request failed: {str(e)}")

    def show_main_screen(self):
        """Display the main screen based on user type"""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttkb.Label(frame, text=f"Welcome, {self.name}!", font=("Helvetica", 20, "bold")).pack(pady=20)
        self.balance_label = ttkb.Label(frame, text=f"Balance: ${self.balance:.2f}")
        self.balance_label.pack(pady=5)


        if self.user_type == "client":
            self.create_client_dashboard(frame)
        elif self.user_type in ["banker", "admin"]:
            self.create_banker_admin_dashboard(frame)

        ttkb.Button(frame, text="Logout", command=self.logout, bootstyle="danger").pack(pady=10)

    def create_client_dashboard(self, parent_frame):
        """Creates the dashboard for client users."""

        # Transaction Form
        transaction_frame = ttkb.Labelframe(parent_frame, text="New Transaction", padding=10)
        transaction_frame.pack(fill="x", pady=10)

        # Transaction Type
        ttkb.Label(transaction_frame, text="Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        transaction_type_combo = ttkb.Combobox(transaction_frame, textvariable=self.transaction_type_var,
                                              values=["deposit", "withdraw", "transfer"], state="readonly")
        transaction_type_combo.grid(row=0, column=1, padx=5, pady=5)
        transaction_type_combo.bind("<<ComboboxSelected>>", self.toggle_transfer_fields)

        # Amount
        ttkb.Label(transaction_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttkb.Entry(transaction_frame, textvariable=self.transaction_amount_var).grid(row=1, column=1, padx=5, pady=5)

        # Category
        ttkb.Label(transaction_frame, text="Category:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttkb.Combobox(transaction_frame, textvariable=self.transaction_category_var,
                      values=self.get_categories(), state="readonly").grid(row=2, column=1, padx=5, pady=5)

        # Recipient Email (for transfers)
        self.recipient_email_label = ttkb.Label(transaction_frame, text="Recipient Email:")
        self.recipient_email_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.recipient_email_entry = ttkb.Entry(transaction_frame, textvariable=self.transaction_recipient_email_var)
        self.recipient_email_entry.grid(row=3, column=1, padx=5, pady=5)
        self.toggle_transfer_fields(None)  # Initially hide

        # Description
        ttkb.Label(transaction_frame, text="Description:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttkb.Entry(transaction_frame, textvariable=self.transaction_description_var).grid(row=4, column=1, padx=5, pady=5)


        # Submit Button
        ttkb.Button(transaction_frame, text="Submit Transaction", command=self.submit_transaction, bootstyle="primary").grid(row=5, column=0, columnspan=2, pady=10)

        # View Transactions Button
        ttkb.Button(parent_frame, text="View Transactions", command=self.view_transactions, bootstyle="info").pack(pady=10)

        # Analytics Buttons
        ttkb.Button(parent_frame, text="Spending Trends", command=self.show_spending_trends, bootstyle="success").pack(pady=5)
        ttkb.Button(parent_frame, text="Balance Alerts", command=self.check_balance_alerts, bootstyle="warning").pack(pady=5)


    def toggle_transfer_fields(self, event):
        """Show/hide recipient email field based on transaction type."""
        if self.transaction_type_var.get() == "transfer":
            self.recipient_email_label.grid()
            self.recipient_email_entry.grid()
        else:
            self.recipient_email_label.grid_remove()
            self.recipient_email_entry.grid_remove()
            self.transaction_recipient_email_var.set("")  # Clear the field

    def get_categories(self):
        """Fetch categories from the backend."""
        try:
            response = requests.get(f"{API_URL}/categories", headers={"Authorization": f"Bearer {self.token}"}, timeout=5)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            categories_data = response.json()
            if categories_data.get("success"):
                return [category["name"] for category in categories_data["categories"]]
            else:
                messagebox.showerror("Error", categories_data["message"])
                logger.warning(f"Failed to fetch categories: {categories_data['message']}")
                return []
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to fetch categories")
            logger.error(f"Failed to fetch categories: {str(e)}")
            return []

    def submit_transaction(self):
        """Submit a transaction to the backend."""
        transaction_type = self.transaction_type_var.get()
        try:
            amount = float(self.transaction_amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return

        category = self.transaction_category_var.get()
        recipient_email = self.transaction_recipient_email_var.get() if transaction_type == "transfer" else None
        description = self.transaction_description_var.get()

        transaction_data = {
            "transaction_type": transaction_type,
            "amount": amount,
            "category": category,
            "recipient_email": recipient_email,
            "description": description
        }

        try:
            response = requests.post(
                f"{API_URL}/transaction",
                headers={"Authorization": f"Bearer {self.token}"},
                json=transaction_data,
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                messagebox.showinfo("Success", data["message"])
                self.balance = data["new_balance"]  # Update balance
                self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
                logger.info(f"Transaction successful: {transaction_data}")
                # Clear transaction form
                self.transaction_amount_var.set("")
                self.transaction_category_var.set("")
                self.transaction_recipient_email_var.set("")
                self.transaction_description_var.set("")

            else:
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Transaction failed: {data['message']}")
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to submit transaction")
            logger.error(f"Transaction request failed: {str(e)}")

    def view_transactions(self):
        """Display transaction history."""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttkb.Label(frame, text="Transaction History", font=("Helvetica", 20, "bold")).pack(pady=20)

        # Date Filter
        date_filter_frame = ttkb.Labelframe(frame, text="Filter by Date", padding=10)
        date_filter_frame.pack(fill="x", pady=10)

        ttkb.Label(date_filter_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttkb.Entry(date_filter_frame, textvariable=self.start_date_var).grid(row=0, column=1, padx=5, pady=5)

        ttkb.Label(date_filter_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttkb.Entry(date_filter_frame, textvariable=self.end_date_var).grid(row=1, column=1, padx=5, pady=5)

        ttkb.Button(date_filter_frame, text="Filter", command=self.load_transactions, bootstyle="info").grid(row=0, column=2, rowspan=2, padx=5, pady=5)


        # Transaction Treeview
        self.transactions_tree = ttkb.Treeview(frame, columns=("ID", "Type", "Amount", "Category", "Date", "Recipient", "Description"), show="headings")
        self.transactions_tree.heading("ID", text="ID")
        self.transactions_tree.heading("Type", text="Type")
        self.transactions_tree.heading("Amount", text="Amount")
        self.transactions_tree.heading("Category", text="Category")
        self.transactions_tree.heading("Date", text="Date")
        self.transactions_tree.heading("Recipient", text="Recipient")
        self.transactions_tree.heading("Description", text="Description") # Added description

        self.transactions_tree.column("ID", width=50, anchor="center")
        self.transactions_tree.column("Type", width=80, anchor="center")
        self.transactions_tree.column("Amount", width=80, anchor="center")
        self.transactions_tree.column("Category", width=100, anchor="center")
        self.transactions_tree.column("Date", width=100, anchor="center")
        self.transactions_tree.column("Recipient", width=120, anchor="center")
        self.transactions_tree.column("Description", width=150, anchor="center") # Added description column

        self.transactions_tree.pack(expand=True, fill="both", pady=10)

        # Back Button
        ttkb.Button(frame, text="Back", command=self.show_main_screen, bootstyle="secondary").pack(pady=10)

        self.load_transactions()  # Load transactions on initial display


    def load_transactions(self):
        """Load transactions from the backend and populate the Treeview."""

        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()

        try:
            # Validate date format
            if start_date:
                datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")


            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            response = requests.get(
                f"{API_URL}/transactions",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params,
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                # Clear existing transactions
                for item in self.transactions_tree.get_children():
                    self.transactions_tree.delete(item)

                for transaction in data["transactions"]:
                    self.transactions_tree.insert("", "end", values=(
                        transaction["transaction_id"],
                        transaction["transaction_type"],
                        f"${transaction['amount']:.2f}",
                        transaction["category"],
                        transaction["transaction_date"],
                        transaction.get("recipient_email", ""),  # Handle potential missing key
                        transaction.get("description", "") # Handle potential missing description
                    ))
                logger.info(f"Loaded {len(data['transactions'])} transactions")
            else:
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Failed to load transactions: {data['message']}")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to load transactions")
            logger.error(f"Failed to load transactions: {str(e)}")

    def show_spending_trends(self):
        """Display spending trends in a pie chart."""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttkb.Label(frame, text="Spending Trends", font=("Helvetica", 20, "bold")).pack(pady=20)

        # Period Selection
        period_var = tk.StringVar(value="all")
        ttkb.Label(frame, text="Select Period:").pack(pady=5)
        ttkb.Combobox(frame, textvariable=period_var, values=["all", "month", "year"], state="readonly").pack(pady=5)
        ttkb.Button(frame, text="Generate Chart", command=lambda: self.generate_spending_chart(period_var.get()), bootstyle="success").pack(pady=10)

        # Placeholder for the chart
        self.chart_canvas = tk.Canvas(frame)
        self.chart_canvas.pack(expand=True, fill="both")

        ttkb.Button(frame, text="Back", command=self.show_main_screen, bootstyle="secondary").pack(pady=10)

    def generate_spending_chart(self, period):
        """Generate and display the spending trends pie chart."""
        try:
            response = requests.get(
                f"{API_URL}/analytics/spending_trends",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"period": period},
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                trends = data["spending_trends"]
                if not trends:
                    messagebox.showinfo("Info", "No spending data available for the selected period.")
                    return

                categories = list(trends.keys())
                amounts = list(trends.values())

                # Create pie chart
                fig = Figure(figsize=(6, 5), dpi=100)
                ax = fig.add_subplot(111)
                ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
                ax.set_title(f"Spending Trends ({period.capitalize()})")

                # Embed in Tkinter window
                for item in self.chart_canvas.find_all():  # Clear previous chart
                    self.chart_canvas.delete(item)
                canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
                canvas.draw()
                canvas.get_tk_widget().pack(expand=True, fill="both")
                logger.info(f"Generated spending trends chart for period: {period}")

            else:
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Failed to generate spending trends chart: {data['message']}")
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to generate spending trends chart")
            logger.error(f"Failed to generate spending trends chart: {str(e)}")

    def check_balance_alerts(self):
        """Check for balance alerts and display a message."""
        try:
            response = requests.get(
                f"{API_URL}/analytics/balance_alerts",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                messagebox.showinfo("Balance Alert", data["message"])
                logger.info(f"Balance alert checked: {data['message']}")
            else:
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Failed to check balance alerts: {data['message']}")
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to check balance alerts")
            logger.error(f"Failed to check balance alerts: {str(e)}")


    def create_banker_admin_dashboard(self, parent_frame):
        """Creates the dashboard for banker and admin users."""

        # Manage Clients Button
        ttkb.Button(parent_frame, text="Manage Clients", command=self.manage_clients, bootstyle="info").pack(pady=10)
        ttkb.Button(parent_frame, text="View All Transactions", command=self.view_all_transactions, bootstyle="info").pack(pady=10)


    def manage_clients(self):
        """Display the client management screen."""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttkb.Label(frame, text="Manage Clients", font=("Helvetica", 20, "bold")).pack(pady=20)

        try:
            response = requests.get(
                f"{API_URL}/clients",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            data = response.json()

            if not data.get("success"):
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Failed to fetch clients: {data['message']}")
                self.show_main_screen()
                return

            clients = data["clients"]
            self.clients_tree = ttkb.Treeview(frame, columns=("ID", "Name", "Email", "Balance"), show="headings")
            self.clients_tree.heading("ID", text="User ID")
            self.clients_tree.heading("Name", text="Name")
            self.clients_tree.heading("Email", text="Email")
            self.clients_tree.heading("Balance", text="Balance")

            self.clients_tree.column("ID", width=50, anchor="center")
            self.clients_tree.column("Name", width=150, anchor="center")
            self.clients_tree.column("Email", width=200, anchor="center")
            self.clients_tree.column("Balance", width=100, anchor="center")

            self.clients_tree.pack(expand=True, fill="both", pady=10)

            for client in clients:
                self.clients_tree.insert("", "end", values=(
                    client["user_id"],
                    f"{client['first_name']} {client['last_name']}",  # Combine first and last name
                    client["email"],
                    f"${client['balance']:.2f}"
                ))

            # Deposit Form
            deposit_frame = ttkb.Labelframe(frame, text="Deposit for Client", padding=10)
            deposit_frame.pack(fill="x", pady=10)

            ttkb.Label(deposit_frame, text="Client ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            ttkb.Entry(deposit_frame, textvariable=self.client_id_var).grid(row=0, column=1, padx=5, pady=5)

            ttkb.Label(deposit_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            ttkb.Entry(deposit_frame, textvariable=self.deposit_amount_var).grid(row=1, column=1, padx=5, pady=5)

            ttkb.Button(deposit_frame, text="Deposit", command=self.deposit_for_client, bootstyle="success").grid(row=0, column=2, rowspan=2, padx=5, pady=5)


            ttkb.Button(frame, text="Back", command=self.show_main_screen, bootstyle="secondary").pack(pady=10)

        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to fetch clients")
            logger.error(f"Failed to fetch clients: {str(e)}")
            self.show_main_screen()

    def deposit_for_client(self):
        """Deposit money for a client."""
        try:
            client_id = int(self.client_id_var.get())
            amount = float(self.deposit_amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid client ID or amount")
            return

        try:
            response = requests.post(
                f"{API_URL}/deposit_for_client",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"user_id": client_id, "amount": amount},
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                messagebox.showinfo("Success", f"Deposited ${amount:.2f} for client {client_id}")
                logger.info(f"Deposited ${amount:.2f} for client {client_id}")
                # Refresh client list
                self.manage_clients()
                # Clear input fields
                self.client_id_var.set("")
                self.deposit_amount_var.set("")
            else:
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Deposit failed: {data['message']}")
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to deposit for client")
            logger.error(f"Deposit request failed: {str(e)}")

    def view_all_transactions(self):
        """Display all transactions (for bankers/admins)."""
        self.clear_screen()

        frame = ttkb.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttkb.Label(frame, text="All Transactions", font=("Helvetica", 20, "bold")).pack(pady=20)

        # Date Filter (same as in view_transactions)
        date_filter_frame = ttkb.Labelframe(frame, text="Filter by Date", padding=10)
        date_filter_frame.pack(fill="x", pady=10)

        ttkb.Label(date_filter_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttkb.Entry(date_filter_frame, textvariable=self.start_date_var).grid(row=0, column=1, padx=5, pady=5)

        ttkb.Label(date_filter_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttkb.Entry(date_filter_frame, textvariable=self.end_date_var).grid(row=1, column=1, padx=5, pady=5)

        ttkb.Button(date_filter_frame, text="Filter", command=self.load_all_transactions, bootstyle="info").grid(row=0, column=2, rowspan=2, padx=5, pady=5)

        # All Transactions Treeview (similar to view_transactions, but with user email)
        self.all_transactions_tree = ttkb.Treeview(frame, columns=("ID", "User", "Type", "Amount", "Category", "Date", "Description"), show="headings")
        self.all_transactions_tree.heading("ID", text="ID")
        self.all_transactions_tree.heading("User", text="User Email")
        self.all_transactions_tree.heading("Type", text="Type")
        self.all_transactions_tree.heading("Amount", text="Amount")
        self.all_transactions_tree.heading("Category", text="Category")
        self.all_transactions_tree.heading("Date", text="Date")
        self.all_transactions_tree.heading("Description", text="Description")

        self.all_transactions_tree.column("ID", width=50, anchor="center")
        self.all_transactions_tree.column("User", width=
        self.all_transactions_tree.column("ID", width=50, anchor="center")
        self.all_transactions_tree.column("User", width=150, anchor="center")
        self.all_transactions_tree.column("Type", width=80, anchor="center")
        self.all_transactions_tree.column("Amount", width=80, anchor="center")
        self.all_transactions_tree.column("Category", width=100, anchor="center")
        self.all_transactions_tree.column("Date", width=100, anchor="center")
        self.all_transactions_tree.column("Description", width=150, anchor="center")

        self.all_transactions_tree.pack(expand=True, fill="both", pady=10)

        ttkb.Button(frame, text="Back", command=self.show_main_screen, bootstyle="secondary").pack(pady=10)

        self.load_all_transactions() # Load on initial display

    def load_all_transactions(self):
        """Load all transactions from the backend (for bankers/admins)."""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()

        try:
            # Validate date format
            if start_date:
                datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")

            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            response = requests.get(
                f"{API_URL}/all_transactions",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params,
                timeout=5
            )
            data = response.json()

            if data.get("success"):
                # Clear existing transactions
                for item in self.all_transactions_tree.get_children():
                    self.all_transactions_tree.delete(item)

                for transaction in data["transactions"]:
                    self.all_transactions_tree.insert("", "end", values=(
                        transaction["transaction_id"],
                        transaction["user_email"],
                        transaction["transaction_type"],
                        f"${transaction['amount']:.2f}",
                        transaction["category"],
                        transaction["transaction_date"],
                        transaction.get("description", "") # Handle missing description
                    ))
                logger.info(f"Loaded {len(data['transactions'])} all transactions")
            else:
                messagebox.showerror("Error", data["message"])
                logger.warning(f"Failed to load all transactions: {data['message']}")

        except ValueError:
            messagebox.showerror("Error", "Invalid date format.  Please use YYYY-MM-DD.")
        except requests.RequestException as e:
            messagebox.showerror("Error", "Failed to load all transactions")
            logger.error(f"Failed to load all transactions: {str(e)}")


    def logout(self):
        """Logout user"""
        self.token = None
        self.user_id = None
        self.user_type = None
        self.name = None
        self.email = None
        self.balance = 0.0
        self.banker_id = None
        logger.info("User logged out")
        self.show_login_screen()

if __name__ == "__main__":
    root = ttkb.Window()
    app = BudgetBuddyApp(root)
    root.mainloop()
