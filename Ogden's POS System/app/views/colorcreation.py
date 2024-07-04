import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from tkcolorpicker import askcolor

class ColorListCreationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Color List")
        self.geometry("400x300")  # Set a default size for the window
        self.create_widgets()

    def create_widgets(self):
        # Color Name Entry
        ttk.Label(self, text="Color Name:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
        self.color_name_entry = ttk.Entry(self)
        self.color_name_entry.grid(column=1, row=0, padx=10, pady=5, sticky='w')

        # Color Picker Button
        self.color_button = ttk.Button(self, text="Select Color", command=self.select_color)
        self.color_button.grid(column=0, row=1, padx=10, pady=5, sticky='w')

        # Color Display
        self.color_display = tk.Canvas(self, width=50, height=25, bg="white", bd=2, relief="sunken")
        self.color_display.grid(column=1, row=1, padx=10, pady=5, sticky='w')

        # Save Button
        self.save_button = ttk.Button(self, text="Save Color", command=self.save_color)
        self.save_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky='ew')

        # Color List Display
        self.color_listbox = tk.Listbox(self, height=10)
        self.color_listbox.grid(column=0, row=3, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.load_colors()

    def select_color(self):
        color = askcolor()[1]
        if color:
            self.selected_color = color
            self.color_display.config(bg=color)

    def save_color(self):
        color_name = self.color_name_entry.get()
        if not color_name or not hasattr(self, 'selected_color'):
            messagebox.showerror("Error", "Please enter a color name and select a color.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        # Check for duplicate color names or hex values
        cursor.execute('SELECT COUNT(*) FROM colors WHERE name = ? OR hex_value = ?', (color_name, self.selected_color))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "A color with this name or hex value already exists.")
            conn.close()
            return

        cursor.execute('''
            INSERT INTO colors (name, hex_value)
            VALUES (?, ?)
        ''', (color_name, self.selected_color))
        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_colors()

    def clear_inputs(self):
        self.color_name_entry.delete(0, tk.END)
        self.color_display.config(bg="white")

    def load_colors(self):
        self.color_listbox.delete(0, tk.END)
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, hex_value FROM colors")
        colors = cursor.fetchall()
        conn.close()

        for color in colors:
            self.color_listbox.insert(tk.END, f"{color[0]}: {color[1]}")

if __name__ == "__main__":
    def initialize_db():
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hex_value TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    initialize_db()

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = ColorListCreationWindow(root)
    app.mainloop()
