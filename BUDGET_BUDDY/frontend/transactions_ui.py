# 💵 Transactions UI: Provides an interface to add/view transactions
# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # Handles API calls to backend
from config import API_URL  # Backend URL configuration

# =============================
# 📌 Transactions UI Class
# =============================
class TransactionsUI:
    def __init__(self, root, token):
        """
        Initializes the transactions dashboard.

        - root: Tkinter root window
        - token: JWT authentication token
        """
        self.root = root
        self.root.title("Transactions - Budget Buddy")
        self.root.geometry("600x400")

        self.token = token  # Store authentication token

        self.create_transactions_dashboard()

    # =============================
    # 📌 Create Transactions Dashboard
    # =============================
    def create_transactions_dashboard(self):
        """
        Displays the main transaction management options.
        """
        self.clear_window()
        tk.Label(self.root, text="Transactions", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.root, text="View Transaction History", command=self.view_transaction_history).pack(pady=5)
        ttk.Button(self.root, text="Add New Transaction", command=self.add_transaction).pack(pady=5)
        ttk.Button(self.root, text="Delete Transaction", command=self.delete_transaction).pack(pady=5)

        ttk.Button(self.root, text="Back", command=self.root.destroy).pack(pady=10)

    # =============================
    # 📌 View Transaction History
    # =============================
    def view_transaction_history(self):
        """
        Fetches and displays the transaction history for a selected account.
        """
        self.clear_window()
        tk.Label(self.root, text="Transaction History", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Account ID:").pack()
        self.account_id_entry = tk.Entry(self.root)
        self.account_id_entry.pack()

        ttk.Button(self.root, text="Get History", command=self.fetch_transaction_history).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_transactions_dashboard).pack()

    def fetch_transaction_history(self):
        """
        Processes the request for transaction history.
        """
        account_id = self.account_id_entry.get()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/transactions/history?account_id={account_id}", headers=headers)

        if response.status_code == 200:
            transactions = response.json()["transactions"]
            self.display_transaction_history(transactions)
        else:
            messagebox.showerror("Error", "Failed to retrieve transaction history")

    def display_transaction_history(self, transactions):
        """
        Displays fetched transactions in the UI.
        """
        self.clear_window()
        tk.Label(self.root, text="Transaction History", font=("Arial", 16)).pack(pady=10)

        for txn in transactions:
            ttk.Label(self.root, text=f"{txn['transaction_type']} - ${txn['amount']} - {txn['category']}").pack()

        ttk.Button(self.root, text="Back", command=self.create_transactions_dashboard).pack(pady=10)

    # =============================
    # 📌 Add a New Transaction
    # =============================
    def add_transaction(self):
        """
        Provides UI for adding a new transaction.
        """
        self.clear_window()
        tk.Label(self.root, text="Add New Transaction", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Account ID:").pack()
        self.account_id_entry = tk.Entry(self.root)
        self.account_id_entry.pack()

        tk.Label(self.root, text="Amount:").pack()
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack()

        tk.Label(self.root, text="Transaction Type (deposit/withdrawal/transfer):").pack()
        self.transaction_type_entry = tk.Entry(self.root)
        self.transaction_type_entry.pack()

        tk.Label(self.root, text="Category:").pack()
        self.category_entry = tk.Entry(self.root)
        self.category_entry.pack()

        tk.Label(self.root, text="Description:").pack()
        self.description_entry = tk.Entry(self.root)
        self.description_entry.pack()

        ttk.Button(self.root, text="Submit", command=self.process_add_transaction).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_transactions_dashboard).pack()

    def process_add_transaction(self):
        """
        Processes the transaction addition request.
        """
        account_id = self.account_id_entry.get()
        amount = self.amount_entry.get()
        transaction_type = self.transaction_type_entry.get()
        category = self.category_entry.get()
        description = self.description_entry.get()

        if not (account_id and amount and transaction_type):
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "account_id": account_id,
            "amount": float(amount),
            "transaction_type": transaction_type,
            "category": category,
            "description": description
        }
        response = requests.post(f"{API_URL}/transactions/add", json=data, headers=headers)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Transaction added successfully")
            self.create_transactions_dashboard()
        else:
            messagebox.showerror("Error", "Failed to add transaction")

    # =============================
    # 📌 Delete a Transaction
    # =============================
    def delete_transaction(self):
        """
        Provides UI for deleting a transaction.
        """
        self.clear_window()
        tk.Label(self.root, text="Delete Transaction", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Transaction ID:").pack()
        self.transaction_id_entry = tk.Entry(self.root)
        self.transaction_id_entry.pack()

        ttk.Button(self.root, text="Delete", command=self.process_delete_transaction).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_transactions_dashboard).pack()

    def process_delete_transaction(self):
        """
        Processes the transaction deletion request.
        """
        transaction_id = self.transaction_id_entry.get()

        if not transaction_id:
            messagebox.showerror("Error", "Please enter a Transaction ID")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{API_URL}/transactions/{transaction_id}", headers=headers)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Transaction deleted successfully")
            self.create_transactions_dashboard()
        else:
            messagebox.showerror("Error", "Failed to delete transaction")

    # =============================
    # 📌 Clear Window
    # =============================
    def clear_window(self):
        """
        Clears all elements from the window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
