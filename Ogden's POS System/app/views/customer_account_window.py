# customer_account_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import requests
#from app.views.ticket_type import TicketTypeWindow
#from app.views.detailed_ticket import DetailedTicketCreationWindow
#from app.views.quick_ticket import QuickTicketWindow

class CustomerAccountWindow(tk.Toplevel):
    def __init__(self, parent, db_conn, customer_id=None):
        super().__init__(parent)
        self.db_conn = db_conn
        self.customer_id = customer_id
        self.title("Ogden's Dry Clean Program")
        self.geometry("2000x1200")  # Set a default size for the window
        self.create_widgets()
        self.load_ticket_types()
        if self.customer_id:
            self.load_customer_data()

    def create_widgets(self):
        # Next Customer Button
        self.next_customer_button = ttk.Button(self, text="Next Customer", command=self.next_customer)
        self.next_customer_button.grid(column=0, row=0, padx=10, pady=10, sticky='w')

        # Customer Information
        self.customer_info_frame = ttk.LabelFrame(self, text="Customer Information")
        self.customer_info_frame.grid(column=0, row=1, padx=10, pady=10, sticky='w')

        ttk.Label(self.customer_info_frame, text="Last Name:").grid(column=0, row=0, padx=5, pady=5, sticky='w')
        self.last_name_entry = ttk.Entry(self.customer_info_frame)
        self.last_name_entry.grid(column=1, row=0, padx=5, pady=5, sticky='w')
        self.last_name_entry.bind("<FocusOut>", self.save_customer_data)

        ttk.Label(self.customer_info_frame, text="First Name:").grid(column=0, row=1, padx=5, pady=5, sticky='w')
        self.first_name_entry = ttk.Entry(self.customer_info_frame)
        self.first_name_entry.grid(column=1, row=1, padx=5, pady=5, sticky='w')
        self.first_name_entry.bind("<FocusOut>", self.save_customer_data)

        ttk.Label(self.customer_info_frame, text="Phone #:").grid(column=0, row=2, padx=5, pady=5, sticky='w')
        self.phone_entry = ttk.Entry(self.customer_info_frame)
        self.phone_entry.grid(column=1, row=2, padx=5, pady=5, sticky='w')
        self.phone_entry.bind("<FocusOut>", self.save_customer_data)

        ttk.Label(self.customer_info_frame, text="Notes:").grid(column=0, row=3, padx=5, pady=5, sticky='nw')
        self.notes_text = tk.Text(self.customer_info_frame, width=30, height=4)
        self.notes_text.grid(column=1, row=3, padx=5, pady=5, sticky='w')
        self.notes_text.bind("<FocusOut>", self.save_customer_data)

        # Buttons for Ticket Types
        self.ticket_type_buttons_frame = ttk.Frame(self)
        self.ticket_type_buttons_frame.grid(column=0, row=2, padx=10, pady=5, sticky='nsew')

        # Tickets
        columns = ("ticket_id", "customer_id", "date", "ticket_number", "rack", "pieces", "total", "status", "type")
        self.tickets_tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tickets_tree.grid(column=1, row=0, rowspan=3, padx=10, pady=10, sticky='nsew')

        for col in columns:
            self.tickets_tree.heading(col, text=col.replace("_", " ").title())
            self.tickets_tree.column(col, width=100)

        # Configure the grid to make the ticket list window twice as tall
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=2)

        # Buttons
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(column=2, row=0, rowspan=3, padx=10, pady=10, sticky='ns')

        buttons = [
            "View Ticket", "Edit Ticket", "Redo Ticket", "Void Ticket",
            "Assign Tags", "Undo Pickup", "Reprint Cust. Receipt",
            "Reprint Ticket", "Print Tags"
        ]
        for button in buttons:
            ttk.Button(self.buttons_frame, text=button, command=lambda b=button: self.handle_button_click(b)).pack(pady=5, fill='x')

        # Frame for ticket type buttons
        self.ticket_buttons_frame = tk.Frame(self)
        self.ticket_buttons_frame.grid(column=0, row=2, padx=10, pady=10, sticky='nsew')

        # Configure grid for buttons
        self.ticket_buttons_frame.grid_columnconfigure(0, weight=1)
        self.ticket_buttons_frame.grid_columnconfigure(1, weight=1)
        self.ticket_buttons_frame.grid_columnconfigure(2, weight=1)

        # Create ticket type buttons
        self.create_ticket_type_buttons()

        self.control_buttons_frame = ttk.Frame(self)
        self.control_buttons_frame.grid(column=0, row=1, padx=10, pady=10, sticky='nw')

        ttk.Button(self.control_buttons_frame, text="Create Quick Ticket", command=self.create_quick_ticket).pack(pady=5, fill='x')

    def next_customer(self):
        from views.customer_search_window import CustomerSearchWindow  # Import here to avoid circular import
        self.destroy()
        CustomerSearchWindow(self.master, self.db_conn)

    def handle_button_click(self, button):
        # Placeholder for handling button clicks
        messagebox.showinfo(button, f"{button} functionality not yet implemented.")

    def load_customer_data(self):
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT last_name, first_name, phone, notes FROM customers WHERE id = ?", (self.customer_id,))
        customer = cursor.fetchone()
        conn.close()

        if customer:
            self.last_name_entry.insert(0, customer[0])
            self.first_name_entry.insert(0, customer[1])
            self.phone_entry.insert(0, customer[2])
            self.notes_text.insert(tk.END, customer[3])

    def save_customer_data(self, event=None):
        last_name = self.last_name_entry.get()
        first_name = self.first_name_entry.get()
        phone = self.phone_entry.get()
        notes = self.notes_text.get("1.0", tk.END).strip()

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        if self.customer_id:
            cursor.execute('''
                UPDATE customers
                SET last_name = ?, first_name = ?, phone = ?, notes = ?
                WHERE id = ?
            ''', (last_name, first_name, phone, notes, self.customer_id))
        else:
            cursor.execute('''
                INSERT INTO customers (last_name, first_name, phone, notes)
                VALUES (?, ?, ?, ?)
            ''', (last_name, first_name, phone, notes))
            self.customer_id = cursor.lastrowid

        conn.commit()
        conn.close()

    def create_ticket_type_buttons(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, name FROM ticket_types")
        ticket_types = cursor.fetchall()

        row = 0
        col = 0

        for ticket_type_id, ticket_type_name in ticket_types:
            button = ttk.Button(self.ticket_buttons_frame, text=ticket_type_name, command=lambda id=ticket_type_id: self.open_ticket_creation_window(id))
            button.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            col += 1
            if col >= 3:
                col = 0
                row += 1

  #  def open_ticket_creation_window(self, ticket_type_id):
  #      DetailedTicketCreationWindow(self, self.db_conn, self.customer_id, ticket_type_id)

    def load_ticket_types(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, name FROM ticket_types")
        ticket_types = cursor.fetchall()

        for ticket_type in ticket_types:
            button = ttk.Button(self.ticket_type_buttons_frame, text=ticket_type[1], command=lambda tt=ticket_type: self.create_ticket(tt))
            button.pack(side=tk.LEFT, padx=5, pady=5)

    def update_ticket_list(self):
        self.tickets_tree.delete(*self.tickets_tree.get_children())
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT ticket_number, date, status, total FROM tickets WHERE customer_id = ?
        ''', (self.customer_id,))
        tickets = cursor.fetchall()
        for ticket in tickets:
            self.tickets_tree.insert('', 'end', values=ticket)

  #  def create_ticket(self, ticket_type):
   #     DetailedTicketCreationWindow(self, self.db_conn, self.customer_id, ticket_type[0])

    def load_ticket_types(self):
        try:
            response = requests.get('http://127.0.0.1:5000/ticket_types')
            if response.status_code == 200:
                ticket_types = response.json()
                for i in range(3):
                    combobox = getattr(self, f"ticket_type_{i+1}")
                    combobox['values'] = [ticket_type['name'] for ticket_type in ticket_types]
            else:
                messagebox.showerror("Error", "Failed to load ticket types.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")

 #   def create_quick_ticket(self):
 #       QuickTicketWindow(self, self.db_conn)

    def submit_quick_ticket(self):
        quick_ticket = {
            "customer_id": self.customer_id,
            "due_date": self.due_date.get(),
            "tickets": [
                {
                    "ticket_type": getattr(self, "ticket_type_1").get(),
                    "pieces": getattr(self, "pieces_1").get(),
                    "notes": getattr(self, "notes_1").get()
                },
                {
                    "ticket_type": getattr(self, "ticket_type_2").get(),
                    "pieces": getattr(self, "pieces_2").get(),
                    "notes": getattr(self, "notes_2").get()
                },
                {
                    "ticket_type": getattr(self, "ticket_type_3").get(),
                    "pieces": getattr(self, "pieces_3").get(),
                    "notes": getattr(self, "notes_3").get()
                }
            ],
            "overall_notes": self.overall_notes.get()
        }

        try:
            response = requests.post('http://127.0.0.1:5000/quick_tickets', json=quick_ticket)
            if response.status_code == 201:
                messagebox.showinfo("Success", "Quick Ticket created successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to create Quick Ticket.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")

if __name__ == "__main__":
    def create_db_connection(db_path='pos_system.db'):
        conn = sqlite3.connect(db_path)
        return conn

    db_conn = create_db_connection()

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = CustomerAccountWindow(root, db_conn)
    app.mainloop()
