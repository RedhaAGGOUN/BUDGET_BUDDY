# 📈 Reports & Charts : Generates financial reports using Matplotlib
# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # Handles API calls to backend
from config import API_URL  # Backend URL configuration
import matplotlib.pyplot as plt  # For graph visualization

# =============================
# 📌 Reports UI Class
# =============================
class ReportsUI:
    def __init__(self, root, token):
        """
        Initializes the reports dashboard.

        - root: Tkinter root window
        - token: JWT authentication token
        """
        self.root = root
        self.root.title("Financial Reports - Budget Buddy")
        self.root.geometry("600x400")

        self.token = token  # Store authentication token

        self.create_reports_dashboard()

    # =============================
    # 📌 Create Reports Dashboard
    # =============================
    def create_reports_dashboard(self):
        """
        Displays the main report options.
        """
        self.clear_window()
        tk.Label(self.root, text="Financial Reports", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.root, text="Monthly Spending", command=self.view_monthly_spending).pack(pady=5)
        ttk.Button(self.root, text="Yearly Spending", command=self.view_yearly_spending).pack(pady=5)
        ttk.Button(self.root, text="Category Analysis", command=self.view_category_spending).pack(pady=5)
        ttk.Button(self.root, text="Cash Flow Report", command=self.view_cash_flow).pack(pady=5)

        ttk.Button(self.root, text="Back", command=self.root.destroy).pack(pady=10)

    # =============================
    # 📌 View Monthly Spending
    # =============================
    def view_monthly_spending(self):
        """
        Fetches and displays monthly spending data.
        """
        self.clear_window()
        tk.Label(self.root, text="Monthly Spending Report", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Year:").pack()
        self.year_entry = tk.Entry(self.root)
        self.year_entry.pack()

        tk.Label(self.root, text="Month:").pack()
        self.month_entry = tk.Entry(self.root)
        self.month_entry.pack()

        ttk.Button(self.root, text="Get Report", command=self.fetch_monthly_spending).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_reports_dashboard).pack()

    def fetch_monthly_spending(self):
        """
        Processes the request for monthly spending data.
        """
        year = self.year_entry.get()
        month = self.month_entry.get()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/reports/monthly_spending?year={year}&month={month}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            messagebox.showinfo("Monthly Spending", f"Total Spent: ${data['total_spent']}")
        else:
            messagebox.showerror("Error", "Failed to retrieve report")

    # =============================
    # 📌 View Yearly Spending
    # =============================
    def view_yearly_spending(self):
        """
        Fetches and displays yearly spending data.
        """
        self.clear_window()
        tk.Label(self.root, text="Yearly Spending Report", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Year:").pack()
        self.year_entry = tk.Entry(self.root)
        self.year_entry.pack()

        ttk.Button(self.root, text="Get Report", command=self.fetch_yearly_spending).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_reports_dashboard).pack()

    def fetch_yearly_spending(self):
        """
        Processes the request for yearly spending data.
        """
        year = self.year_entry.get()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/reports/yearly_spending?year={year}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.plot_yearly_spending(data["monthly_spending"])
        else:
            messagebox.showerror("Error", "Failed to retrieve report")

    def plot_yearly_spending(self, spending_data):
        """
        Displays a bar chart for yearly spending.
        """
        months = [item["month"] for item in spending_data]
        values = [item["total_spent"] for item in spending_data]

        plt.bar(months, values, color='blue')
        plt.xlabel("Month")
        plt.ylabel("Amount Spent ($)")
        plt.title("Yearly Spending")
        plt.show()

    # =============================
    # 📌 View Category-Based Spending
    # =============================
    def view_category_spending(self):
        """
        Fetches and displays category-based expense data.
        """
        self.clear_window()
        tk.Label(self.root, text="Category Spending Report", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Year:").pack()
        self.year_entry = tk.Entry(self.root)
        self.year_entry.pack()

        tk.Label(self.root, text="Month:").pack()
        self.month_entry = tk.Entry(self.root)
        self.month_entry.pack()

        ttk.Button(self.root, text="Get Report", command=self.fetch_category_spending).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_reports_dashboard).pack()

    def fetch_category_spending(self):
        """
        Processes the request for category spending data.
        """
        year = self.year_entry.get()
        month = self.month_entry.get()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/reports/category_spending?year={year}&month={month}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.plot_category_spending(data["category_spending"])
        else:
            messagebox.showerror("Error", "Failed to retrieve report")

    def plot_category_spending(self, spending_data):
        """
        Displays a pie chart for category-based spending.
        """
        categories = [item["category"] for item in spending_data]
        values = [item["total_spent"] for item in spending_data]

        plt.pie(values, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Category-Based Spending")
        plt.show()

    # =============================
    # 📌 View Cash Flow Report
    # =============================
    def view_cash_flow(self):
        """
        Fetches and displays cash flow data.
        """
        self.clear_window()
        tk.Label(self.root, text="Cash Flow Report", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Year:").pack()
        self.year_entry = tk.Entry(self.root)
        self.year_entry.pack()

        tk.Label(self.root, text="Month:").pack()
        self.month_entry = tk.Entry(self.root)
        self.month_entry.pack()

        ttk.Button(self.root, text="Get Report", command=self.fetch_cash_flow).pack(pady=5)
        ttk.Button(self.root, text="Back", command=self.create_reports_dashboard).pack()

    def fetch_cash_flow(self):
        """
        Processes the request for cash flow data.
        """
        year = self.year_entry.get()
        month = self.month_entry.get()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/reports/cash_flow?year={year}&month={month}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            messagebox.showinfo("Cash Flow Report",
                                f"Income: ${data['total_income']}\n"
                                f"Expenses: ${data['total_expenses']}\n"
                                f"Net Cash Flow: ${data['net_cash_flow']}")
        else:
            messagebox.showerror("Error", "Failed to retrieve report")

    # =============================
    # 📌 Clear Window
    # =============================
    def clear_window(self):
        """
        Clears all elements from the window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

