import tkinter as tk
from tkinter import ttk
from initialize_db import create_db_connection
from customer_account_window import CustomerAccountWindow
import sqlite3

class CustomerSearchWindow(tk.Toplevel):
    def __init__(self, parent, db_conn):
        super().__init__(parent)
        self.db_conn = db_conn
        self.title("Customer Search")
        self.geometry("700x400")
        self.create_widgets()

    def create_widgets(self):

        ttk.Label(self, text="First Name:").grid(row=2, column=0, padx=10, pady=5, sticky='sw')
        self.first_name_entry = ttk.Entry(self)
        self.first_name_entry.grid(column=0, row=3, padx=10, pady=5, sticky='nw')
        self.first_name_entry.bind("<Return>", lambda event: self.search_customers())

        ttk.Label(self, text="Last Name:").grid(row=0, column=0, padx=10, pady=5, sticky='sw')
        self.last_name_entry = ttk.Entry(self)
        self.last_name_entry.grid(column=0, row=1, padx=10, pady=5, sticky='nw')
        self.last_name_entry.bind("<Return>", lambda event: self.search_customers())
        
        ttk.Label(self, text="Phone #:").grid(row=4, column=0, padx=10, pady=5, sticky='sw')
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=5, column=0, padx=10, pady=5, sticky='nw')
        self.phone_entry.bind("<Return>", lambda event: self.search_customers())

        ttk.Label(self, text="Customer Name").grid(column=1, row=0, padx=10, pady=5, sticky='w')
        ttk.Label(self, text="Phone").grid(column=2, row=0, padx=10, pady=5, sticky='w')
        self.result_list = tk.Listbox(self, height=15, width=70)
        self.result_list.grid(column=1, row=1, rowspan=6, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.result_list.bind("<Double-1>", lambda event: self.select_customer())
        
        self.new_customer_button = ttk.Button(self, text="New Customer", command=self.create_new_customer)
        self.new_customer_button.grid(column=0, row=7, padx=10, pady=10, sticky='w')
        
        self.search_button = ttk.Button(self, text="Search", command=self.search_customer)
        self.search_button.grid(column=2, row=7, padx=10, pady=10, sticky='e')

        self.close_button = ttk.Button(self, text="Close", command=self.destroy)
        self.close_button.grid(column=1, row=7, padx=10, pady=10, sticky='e')

    def search_customer(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        phone = self.phone_entry.get()

        cursor = self.db_conn.cursor()
        query = "SELECT * FROM customers WHERE first_name LIKE ? AND last_name LIKE ? AND phone LIKE ?"
        cursor.execute(query, (f"%{first_name}%", f"%{last_name}%", f"%{phone}%"))
        result = cursor.fetchall()

        self.result_list.delete(0, tk.END)
        for customer in result:
            self.result_list.insert(tk.END, f"{customer[1]} {customer[2]} - {customer[3]}")
            
    def select_customer(self):
        selection = self.result_list.get(self.result_list.curselection())
        customer_name, phone = selection.split(" - ")
        last_name, first_name = customer_name.split(" ", 1)

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customers WHERE last_name = ? AND first_name = ? AND phone = ?", (last_name, first_name, phone))
        customer_id = cursor.fetchone()[0]
        conn.close()

        self.destroy()
        CustomerAccountWindow(customer_id)

    def create_new_customer(self):
        self.destroy()
        CustomerAccountWindow()

if __name__ == "__main__":
    conn = create_db_connection()
    root = tk.Tk()
    root.withdraw()
    app = CustomerSearchWindow(root, conn)
    app.mainloop()
