import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3

class CouponsAndDiscountsCreationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Coupons and Discounts List")
        self.geometry("600x400")
        self.create_widgets()
        self.load_items()

    def create_widgets(self):
        # Name Entry
        ttk.Label(self, text="Name:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(column=1, row=0, padx=10, pady=5, sticky='w')

        # Type Selection
        ttk.Label(self, text="Type:").grid(column=0, row=1, padx=10, pady=5, sticky='w')
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(self, textvariable=self.type_var)
        self.type_combobox['values'] = ('Coupon', 'Discount')
        self.type_combobox.grid(column=1, row=1, padx=10, pady=5, sticky='w')

        # Image Selection Button
        self.image_button = ttk.Button(self, text="Select Image (Optional)", command=self.select_image)
        self.image_button.grid(column=0, row=2, padx=10, pady=5, sticky='w')

        # Image Display
        self.image_display = tk.Canvas(self, width=100, height=100, bg="white", bd=2, relief="sunken")
        self.image_display.grid(column=1, row=2, padx=10, pady=5, sticky='w')

        # Save Button
        self.save_button = ttk.Button(self, text="Save Item", command=self.save_item)
        self.save_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10, sticky='ew')

        # Item List Display
        self.item_listbox = tk.Listbox(self, height=10)
        self.item_listbox.grid(column=0, row=4, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.item_listbox.bind("<Double-1>", self.edit_item)

        # Edit and Delete Buttons
        self.edit_button = ttk.Button(self, text="Edit Selected", command=self.edit_item)
        self.edit_button.grid(column=0, row=5, padx=10, pady=5, sticky='w')
        
        self.delete_button = ttk.Button(self, text="Delete Selected", command=self.delete_item)
        self.delete_button.grid(column=1, row=5, padx=10, pady=5, sticky='w')

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.selected_image = file_path
            image = Image.open(file_path)
            image.thumbnail((100, 100))
            self.image_display.image = ImageTk.PhotoImage(image)
            self.image_display.create_image(0, 0, anchor=tk.NW, image=self.image_display.image)

    def save_item(self):
        name = self.name_entry.get()
        item_type = self.type_var.get().lower()
        image_path = getattr(self, 'selected_image', None)
        
        if not name or not item_type:
            messagebox.showerror("Error", "Please enter a name and select a type.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        # Check for duplicate names
        cursor.execute('SELECT COUNT(*) FROM coupons_discounts WHERE name = ? AND type = ?', (name, item_type))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "An item with this name already exists.")
            conn.close()
            return

        cursor.execute('''
            INSERT INTO coupons_discounts (name, type, image)
            VALUES (?, ?, ?)
        ''', (name, item_type, image_path))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_items()

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.type_var.set('')
        self.image_display.delete("all")

    def load_items(self):
        self.item_listbox.delete(0, tk.END)
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, image FROM coupons_discounts")
        self.items = cursor.fetchall()
        conn.close()

        for item in self.items:
            self.item_listbox.insert(tk.END, f"{item[1]} ({item[2]})")

    def edit_item(self, event=None):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to edit.")
            return

        index = selection[0]
        item_id, item_name, item_type, item_image = self.items[index]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, item_name)
        self.type_var.set(item_type.capitalize())
        self.selected_image = item_image

        if item_image:
            image = Image.open(item_image)
            image.thumbnail((100, 100))
            self.image_display.image = ImageTk.PhotoImage(image)
            self.image_display.create_image(0, 0, anchor=tk.NW, image=self.image_display.image)
        else:
            self.image_display.delete("all")

        self.save_button.config(text="Update Item", command=lambda: self.update_item(item_id))

    def update_item(self, item_id):
        name = self.name_entry.get()
        item_type = self.type_var.get().lower()
        image_path = getattr(self, 'selected_image', None)
        
        if not name or not item_type:
            messagebox.showerror("Error", "Please enter a name and select a type.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        # Check for duplicate names
        cursor.execute('SELECT COUNT(*) FROM coupons_discounts WHERE name = ? AND type = ? AND id != ?', (name, item_type, item_id))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "An item with this name already exists.")
            conn.close()
            return

        cursor.execute('''
            UPDATE coupons_discounts
            SET name = ?, type = ?, image = ?
            WHERE id = ?
        ''', (name, item_type, image_path, item_id))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.save_button.config(text="Save Item", command=self.save_item)
        self.load_items()

    def delete_item(self):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        index = selection[0]
        item_id, _, _, _ = self.items[index]

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM coupons_discounts WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

        self.load_items()

if __name__ == "__main__":
    def initialize_db():
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons_discounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,  -- "coupon" or "discount"
                image TEXT
            )
        ''')
        conn.commit()
        conn.close()

    initialize_db()

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = CouponsAndDiscountsCreationWindow(root)
    app.mainloop()
