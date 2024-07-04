import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3

class PatternListCreationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Pattern List")
        self.geometry("600x400")
        self.create_widgets()
        self.load_patterns()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy()
        self.update_parent_state()

    def update_parent_state(self):
        if self.master:
            self.master.attributes("-disabled", False)
            self.master.focus()

    def create_widgets(self):
        # Pattern Name Entry
        ttk.Label(self, text="Pattern Name:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
        self.pattern_name_entry = ttk.Entry(self)
        self.pattern_name_entry.grid(column=1, row=0, padx=10, pady=5, sticky='w')

        # Image Selection Button
        self.image_button = ttk.Button(self, text="Select Image (Optional)", command=self.select_image)
        self.image_button.grid(column=0, row=1, padx=10, pady=5, sticky='w')

        # Image Display
        self.image_display = tk.Canvas(self, width=100, height=100, bg="white", bd=2, relief="sunken")
        self.image_display.grid(column=1, row=1, padx=10, pady=5, sticky='w')

        # Save Button
        self.save_button = ttk.Button(self, text="Save Pattern", command=self.save_pattern)
        self.save_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky='ew')

        # Pattern List Display
        self.pattern_listbox = tk.Listbox(self, height=10)
        self.pattern_listbox.grid(column=0, row=3, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.pattern_listbox.bind("<Double-1>", self.edit_pattern)

        # Edit and Delete Buttons
        self.edit_button = ttk.Button(self, text="Edit Selected", command=self.edit_pattern)
        self.edit_button.grid(column=0, row=4, padx=10, pady=5, sticky='w')
        
        self.delete_button = ttk.Button(self, text="Delete Selected", command=self.delete_pattern)
        self.delete_button.grid(column=1, row=4, padx=10, pady=5, sticky='w')

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.selected_image = file_path
            image = Image.open(file_path)
            image.thumbnail((100, 100))
            self.image_display.image = ImageTk.PhotoImage(image)
            self.image_display.create_image(0, 0, anchor=tk.NW, image=self.image_display.image)

    def save_pattern(self):
        pattern_name = self.pattern_name_entry.get()
        image_path = getattr(self, 'selected_image', None)
        
        if not pattern_name:
            messagebox.showerror("Error", "Please enter a pattern name.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        # Check for duplicate pattern names
        cursor.execute('SELECT COUNT(*) FROM patterns WHERE name = ?', (pattern_name,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "A pattern with this name already exists.")
            conn.close()
            return

        cursor.execute('''
            INSERT INTO patterns (name, image)
            VALUES (?, ?)
        ''', (pattern_name, image_path))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_patterns()

    def clear_inputs(self):
        self.pattern_name_entry.delete(0, tk.END)
        self.image_display.delete("all")

    def load_patterns(self):
        self.pattern_listbox.delete(0, tk.END)
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, image FROM patterns")
        self.patterns = cursor.fetchall()
        conn.close()

        for pattern in self.patterns:
            self.pattern_listbox.insert(tk.END, pattern[1])

    def edit_pattern(self, event=None):
        selection = self.pattern_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a pattern to edit.")
            return

        index = selection[0]
        pattern_id, pattern_name, pattern_image = self.patterns[index]

        self.pattern_name_entry.delete(0, tk.END)
        self.pattern_name_entry.insert(0, pattern_name)
        self.selected_image = pattern_image

        if pattern_image:
            image = Image.open(pattern_image)
            image.thumbnail((100, 100))
            self.image_display.image = ImageTk.PhotoImage(image)
            self.image_display.create_image(0, 0, anchor=tk.NW, image=self.image_display.image)
        else:
            self.image_display.delete("all")

        self.save_button.config(text="Update Pattern", command=lambda: self.update_pattern(pattern_id))

    def update_pattern(self, pattern_id):
        pattern_name = self.pattern_name_entry.get()
        image_path = getattr(self, 'selected_image', None)
        
        if not pattern_name:
            messagebox.showerror("Error", "Please enter a pattern name.")
            return

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()

        # Check for duplicate pattern names
        cursor.execute('SELECT COUNT(*) FROM patterns WHERE name = ? AND id != ?', (pattern_name, pattern_id))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "A pattern with this name already exists.")
            conn.close()
            return

        cursor.execute('''
            UPDATE patterns
            SET name = ?, image = ?
            WHERE id = ?
        ''', (pattern_name, image_path, pattern_id))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.save_button.config(text="Save Pattern", command=self.save_pattern)
        self.load_patterns()

    def delete_pattern(self):
        selection = self.pattern_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a pattern to delete.")
            return

        index = selection[0]
        pattern_id, _, _ = self.patterns[index]

        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM patterns WHERE id = ?', (pattern_id,))
        conn.commit()
        conn.close()

        self.load_patterns()

if __name__ == "__main__":
    def initialize_db():
        conn = sqlite3.connect('pos_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image TEXT
            )
        ''')
        conn.commit()
        conn.close()

    initialize_db()

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = PatternListCreationWindow(root)
    app.mainloop()
