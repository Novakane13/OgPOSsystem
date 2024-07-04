import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3

class GarmentListCreationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Garment List")
        self.geometry("600x400")
        self.create_widgets()
        self.load_garments()

    def create_widgets(self):
        ttk.Label(self, text="Garment Name:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
        self.garment_name_entry = ttk.Entry(self)
        self.garment_name_entry.grid(column=1, row=0, padx=10, pady=5, sticky='w')

        self.image_button = ttk.Button(self, text="Select Image", command=self.select_image)
        self.image_button.grid(column=0, row=1, padx=10, pady=5, sticky='w')

        self.image_display = tk.Canvas(self, width=100, height=100, bg="white", bd=2, relief="sunken")
        self.image_display.grid(column=1, row=1, padx=10, pady=5, sticky='w')

        ttk.Label(self, text="Add Variation:").grid(column=0, row=2, padx=10, pady=5, sticky='w')
        self.variation_entry = ttk.Entry(self)
        self.variation_entry.grid(column=1, row=2, padx=10, pady=5, sticky='w')

        self.add_variation_button = ttk.Button(self, text="Add Variation", command=self.add_variation)
        self.add_variation_button.grid(column=2, row=2, padx=10, pady=5, sticky='w')

        self.variation_listbox = tk.Listbox(self, height=5)
        self.variation_listbox.grid(column=0, row=3, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.save_button = ttk.Button(self, text="Save Garment", command=self.save_garment)
        self.save_button.grid(column=0, row=4, columnspan=3, padx=10, pady=10, sticky='ew')

        self.garment_listbox = tk.Listbox(self, height=10)
        self.garment_listbox.grid(column=0, row=5, columnspan=3, padx=10, pady=10, sticky='nsew')
        self.garment_listbox.bind("<Double-1>", self.edit_garment)

        self.edit_button = ttk.Button(self, text="Edit Selected", command=self.edit_garment)
        self.edit_button.grid(column=0, row=6, padx=10, pady=5, sticky='w')

        self.delete_button = ttk.Button(self, text="Delete Selected", command=self.delete_garment)
        self.delete_button.grid(column=1, row=6, padx=10, pady=5, sticky='w')

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.selected_image = file_path
            image = Image.open(file_path)
            image.thumbnail((100, 100))
            self.image_display.image = ImageTk.PhotoImage(image)
            self.image_display.create_image(0, 0, anchor=tk.NW, image=self.image_display.image)

    def add_variation(self):
        variation_name = self.variation_entry.get()
        if variation_name:
            self.variation_listbox.insert(tk.END, variation_name)
            self.variation_entry.delete(0, tk.END)

    def save_garment(self):
        garment_name = self.garment_name_entry.get()
        if not garment_name or not hasattr(self, 'selected_image'):
            messagebox.showerror("Error", "Please enter a garment name and select an image.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM garments WHERE name = ? OR image = ?', (garment_name, self.selected_image))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "A garment with this name or image already exists.")
            conn.close()
            return

        cursor.execute('''
            INSERT INTO garments (name, image)
            VALUES (?, ?)
        ''', (garment_name, self.selected_image))
        garment_id = cursor.lastrowid

        variations = self.variation_listbox.get(0, tk.END)
        for variation in variations:
            cursor.execute('''
                INSERT INTO variations (garment_id, name)
                VALUES (?, ?)
            ''', (garment_id, variation))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_garments()

    def clear_inputs(self):
        self.garment_name_entry.delete(0, tk.END)
        self.variation_listbox.delete(0, tk.END)
        self.image_display.delete("all")

    def load_garments(self):
        self.garment_listbox.delete(0, tk.END)
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, image FROM garments")
        self.garments = cursor.fetchall()
        conn.close()

        for garment in self.garments:
            self.garment_listbox.insert(tk.END, f"{garment[1]}")

    def edit_garment(self, event=None):
        selection = self.garment_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a garment to edit.")
            return

        index = selection[0]
        garment_id, garment_name, garment_image = self.garments[index]

        self.garment_name_entry.delete(0, tk.END)
        self.garment_name_entry.insert(0, garment_name)
        self.selected_image = garment_image

        image = Image.open(garment_image)
        image.thumbnail((100, 100))
        self.image_display.image = ImageTk.PhotoImage(image)
        self.image_display.create_image(0, 0, anchor=tk.NW, image=self.image_display.image)

        self.variation_listbox.delete(0, tk.END)
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM variations WHERE garment_id = ?", (garment_id,))
        variations = cursor.fetchall()
        conn.close()

        for variation in variations:
            self.variation_listbox.insert(tk.END, variation[0])

        self.save_button.config(text="Update Garment", command=lambda: self.update_garment(garment_id))

    def update_garment(self, garment_id):
        garment_name = self.garment_name_entry.get()
        if not garment_name or not hasattr(self, 'selected_image'):
            messagebox.showerror("Error", "Please enter a garment name and select an image.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM garments WHERE (name = ? OR image = ?) AND id != ?', (garment_name, self.selected_image, garment_id))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "A garment with this name or image already exists.")
            conn.close()
            return

        cursor.execute('''
            UPDATE garments
            SET name = ?, image = ?
            WHERE id = ?
        ''', (garment_name, self.selected_image, garment_id))

        cursor.execute('DELETE FROM variations WHERE garment_id = ?', (garment_id,))
        variations = self.variation_listbox.get(0, tk.END)
        for variation in variations:
            cursor.execute('''
                INSERT INTO variations (garment_id, name)
                VALUES (?, ?)
            ''', (garment_id, variation))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.save_button.config(text="Save Garment", command=self.save_garment)
        self.load_garments()

    def delete_garment(self):
        selection = self.garment_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a garment to delete.")
            return

        index = selection[0]
        garment_id, _, _ = self.garments[index]

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM garments WHERE id = ?', (garment_id,))
        cursor.execute('DELETE FROM variations WHERE garment_id = ?', (garment_id,))
        conn.commit()
        conn.close()

        self.load_garments()

if __name__ == "__main__":
    def initialize_db():
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS garments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                garment_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (garment_id) REFERENCES garments(id)
            )
        ''')
        conn.commit()
        conn.close()

    initialize_db()

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = GarmentListCreationWindow(root)
    app.mainloop()