# 🏦 Banker Dashboard UI: Allows bankers to manage clients
# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # Handles API calls to backend
from config import API_URL  # Backend URL configuration

# =============================
# 📌 Banker Dashboard Class
# =============================
class BankerDashboard:
    def __init__(self, root, token):
        """
        Initializes the banker dashboard.

        - root: Tkinter root window
        - token: JWT authentication token
        """
        self.root = root
        self.root.title("Banker Dashboard")
        self.root.geometry("600x400")

        self.token = token  # Store authentication token

        self.create_dashboard()

    # =============================
    # 📌 Create Banker Dashboard UI
    # =============================
    def create_dashboard(self):
        """
        Displays the banker dashboard with management options.
        """
        self.clear_window()
        tk.Label(self.root, text="Banker Dashboard", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.root, text="View Assigned Clients", command=self.view_clients).pack(pady=5)
        ttk.Button(self.root, text="Assign New Client", command=self.assign_client).pack(pady=5)
        ttk.Button(self.root, text="Perform Transaction for Client", command=self.perform_transaction).pack(pady=5)
        ttk.Button(self.root, text="Remove Client", command=self.remove_client).pack(pady=5)

        ttk.Button(self.root, text="Back", command=self.root.destroy).pack(pady=10)

    # =============================
    # 📌 View Assigned Clients
    # =============================
    def view_clients(self):
        """
        Fetches and displays the list of clients assigned to the banker.
        """
        self.clear_window()
        tk.Label(self.root, text="Assigned Clients", font=("Arial", 16)).pack(pady=10)

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/banker/clients", headers=headers)

        if response.status_code == 200:
            clients = response.json()["clients"]
            for client in clients:
                ttk.Label(self.root, text=f"{client['name']} - {client['email']}").pack()
        else:
            messagebox.showerror("Error", "Failed to retrieve clients")

        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack(pady=10)

    # =============================
    # 📌 Assign a New Client
    # =============================
    def assign_client(self):
        """
        Provides UI for assigning a new client to the banker.
        """
        self.clear_window()
        tk.Label(self.root, text="Assign a New Client", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Client ID:").pack()
        self.client_id_entry = tk.Entry(self.root)
        self.client_id_entry.pack()

        ttk.Button(self.root, text="Assign", command=self.process_assign_client).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack()

    def process_assign_client(self):
        """
        Sends the client assignment request to the backend.
        """
        client_id = self.client_id_entry.get()
        if not client_id:
            messagebox.showerror("Error", "Please enter a Client ID")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{API_URL}/banker/assign_client", json={"client_id": client_id}, headers=headers)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Client assigned successfully")
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Failed to assign client")

    # =============================
    # 📌 Perform a Transaction for a Client
    # =============================
    def perform_transaction(self):
        """
        Provides UI for performing a transaction for a client.
        """
        self.clear_window()
        tk.Label(self.root, text="Perform Transaction", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Client ID:").pack()
        self.client_id_entry = tk.Entry(self.root)
        self.client_id_entry.pack()

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

        ttk.Button(self.root, text="Submit", command=self.process_transaction).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack()

    def process_transaction(self):
        """
        Sends the transaction request to the backend.
        """
        client_id = self.client_id_entry.get()
        account_id = self.account_id_entry.get()
        amount = self.amount_entry.get()
        transaction_type = self.transaction_type_entry.get()
        category = self.category_entry.get()
        description = self.description_entry.get()

        if not (client_id and account_id and amount and transaction_type):
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "client_id": client_id,
            "account_id": account_id,
            "amount": float(amount),
            "transaction_type": transaction_type,
            "category": category,
            "description": description
        }
        response = requests.post(f"{API_URL}/banker/transaction", json=data, headers=headers)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Transaction completed successfully")
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Failed to perform transaction")

    # =============================
    # 📌 Remove an Assigned Client
    # =============================
    def remove_client(self):
        """
        Provides UI for removing an assigned client.
        """
        self.clear_window()
        tk.Label(self.root, text="Remove a Client", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Client ID:").pack()
        self.client_id_entry = tk.Entry(self.root)
        self.client_id_entry.pack()

        ttk.Button(self.root, text="Remove", command=self.process_remove_client).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_dashboard).pack()

    def process_remove_client(self):
        """
        Sends the client removal request to the backend.
        """
        client_id = self.client_id_entry.get()
        if not client_id:
            messagebox.showerror("Error", "Please enter a Client ID")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{API_URL}/banker/remove_client", json={"client_id": client_id}, headers=headers)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Client removed successfully")
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Failed to remove client")

    # =============================
    # 📌 Clear Window
    # =============================
    def clear_window(self):
        """
        Clears all elements from the window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
