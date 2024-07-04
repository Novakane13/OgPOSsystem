import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from initialize_db import create_db_connection

class TicketTypeCreationWindow(tk.Toplevel):
    def __init__(self, parent, db_conn):
        super().__init__(parent)
        self.db_conn = db_conn
        self.title("Ticket Type Creation")
        self.geometry("2000x1200")  # Set a default size for the window

        self.cursor = self.db_conn.cursor()

        self.create_widgets()
        self.refresh_color_list()  # Refresh color list on initialization
        self.refresh_garment_list()  # Refresh garment list on initialization
        self.refresh_pattern_list()  # Refresh pattern list on initialization
        self.refresh_coupons_discounts_list()  # Refresh coupons and discounts list on initialization
        self.refresh_upcharges_list()  # Refresh upcharges list on initialization
        self.refresh_textures_list()  # Refresh textures list on initialization
        self.refresh_ticket_types_list()  # Refresh ticket types list on initialization

    def create_widgets(self):
        # Name of Ticket Type
        ttk.Label(self, text="Name of Ticket Type").grid(column=0, row=0, padx=10, pady=5, sticky='w')
        self.ticket_type_entry = ttk.Entry(self)
        self.ticket_type_entry.grid(column=1, row=0, padx=10, pady=5, sticky='w')

        # Large Empty Box for Garment Selection
        self.garment_selection_frame = ttk.LabelFrame(self, text="Garments for this ticket type", relief=tk.SUNKEN, borderwidth=1)
        self.garment_selection_frame.grid(column=0, row=1, columnspan=2, rowspan=4, padx=10, pady=10, sticky="nsew")
        self.garment_selection_frame.grid_propagate(False)
        self.garment_selection_frame.config(width=300, height=400)

        self.selected_garments_listbox = tk.Listbox(self.garment_selection_frame)
        self.selected_garments_listbox.pack(fill=tk.BOTH, expand=True)
        self.selected_garments_listbox.bind("<Button-3>", self.show_garment_context_menu)

        # Garments List
        self.garment_list_frame = ttk.LabelFrame(self, text="Garment List")
        self.garment_list_frame.grid(column=2, row=1, padx=10, pady=10, sticky='nsew')
        self.garments_listbox = tk.Listbox(self.garment_list_frame)
        self.garments_listbox.pack(fill=tk.BOTH, expand=True)
        self.garments_listbox.bind("<Double-1>", self.add_selected_garment)

        # Colors with Checkboxes
        self.color_list_frame = ttk.LabelFrame(self, text="Colors List")
        self.color_list_frame.grid(column=3, row=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Patterns with Checkboxes
        self.pattern_list_frame = ttk.LabelFrame(self, text="Patterns List")
        self.pattern_list_frame.grid(column=4, row=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Upcharges with Checkboxes
        self.upcharges_list_frame = ttk.LabelFrame(self, text="Upcharges List")
        self.upcharges_list_frame.grid(column=5, row=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Discounts/Coupons with Checkboxes
        self.coupons_discounts_list_frame = ttk.LabelFrame(self, text="Discounts/Coupons List")
        self.coupons_discounts_list_frame.grid(column=6, row=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Textures with Checkboxes
        self.textures_list_frame = ttk.LabelFrame(self, text="Textures List")
        self.textures_list_frame.grid(column=7, row=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Save Button
        self.save_button = ttk.Button(self, text="Save Ticket Type", command=self.save_ticket_type)
        self.save_button.grid(column=0, row=8, columnspan=6, padx=10, pady=10, sticky='ew')

        # Ticket Types List Frame
        self.ticket_types_frame = ttk.LabelFrame(self, text="Saved Ticket Types")
        self.ticket_types_frame.grid(column=0, row=9, columnspan=8, padx=10, pady=10, sticky="nsew")

        self.ticket_types_listbox = tk.Listbox(self.ticket_types_frame)
        self.ticket_types_listbox.pack(fill=tk.BOTH, expand=True)
        self.ticket_types_listbox.bind("<Double-1>", self.edit_ticket_type)

        self.edit_button = ttk.Button(self.ticket_types_frame, text="Edit Selected", command=self.edit_selected_item)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = ttk.Button(self.ticket_types_frame, text="Delete Selected", command=self.delete_selected_item)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Context menu for removing selected garments
        self.garment_context_menu = tk.Menu(self, tearoff=0)
        self.garment_context_menu.add_command(label="Remove", command=self.remove_selected_garment)

    def create_listbox_frame(self, label_text, items, column, rowspan):
        frame = ttk.LabelFrame(self, text=label_text)
        frame.grid(column=column, row=2, rowspan=rowspan, padx=10, pady=10, sticky="nsew")
        checkboxes = []
        for item in items:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(frame, text=item, variable=var)
            cb.pack(anchor='w')
            checkboxes.append(var)
        add_all_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Add All", variable=add_all_var, command=lambda: self.add_all_items(checkboxes, add_all_var)).pack(anchor='w')
        setattr(self, f"{label_text.replace(' ', '_').lower()}_checkboxes", checkboxes)
        setattr(self, f"{label_text.replace(' ', '_').lower()}_add_all", add_all_var)

    def add_all_items(self, checkboxes, add_all_var):
        for var in checkboxes:
            var.set(add_all_var.get())

    def refresh_color_list(self):
        # Clear previous widgets in the frame
        for widget in self.color_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT name, hex_value FROM colors")
        colors = self.cursor.fetchall()

        self.colors = colors
        self.colors_list_checkboxes = []
        for index, color in enumerate(colors):
            color_name, color_value = color
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.color_list_frame, text=color_name, variable=var)
            cb.pack(anchor='w')
            self.colors_list_checkboxes.append(var)

    def refresh_garment_list(self):
        self.garments_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT id, name, image FROM garments")
        self.garments = self.cursor.fetchall()

        for garment in self.garments:
            self.garments_listbox.insert(tk.END, garment[1])

    def refresh_pattern_list(self):
        # Clear previous widgets in the frame
        for widget in self.pattern_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT name, image FROM patterns")
        patterns = self.cursor.fetchall()

        self.patterns = patterns
        self.patterns_list_checkboxes = []
        for index, pattern in enumerate(patterns):
            pattern_name, pattern_image = pattern
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.pattern_list_frame, text=pattern_name, variable=var)
            cb.pack(anchor='w')
            self.patterns_list_checkboxes.append(var)

    def refresh_coupons_discounts_list(self):
        # Clear previous widgets in the frame
        for widget in self.coupons_discounts_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT name, type, image FROM coupons_discounts")
        coupons_discounts = self.cursor.fetchall()

        self.coupons_discounts = coupons_discounts
        self.coupons_discounts_list_checkboxes = []
        for index, item in enumerate(coupons_discounts):
            item_name, item_type, item_image = item
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.coupons_discounts_list_frame, text=f"{item_name} ({item_type})", variable=var)
            cb.pack(anchor='w')
            self.coupons_discounts_list_checkboxes.append(var)

    def refresh_upcharges_list(self):
        # Clear previous widgets in the frame
        for widget in self.upcharges_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT name, price, image FROM upcharges")
        upcharges = self.cursor.fetchall()

        self.upcharges = upcharges
        self.upcharges_list_checkboxes = []
        for index, item in enumerate(upcharges):
            item_name, item_price, item_image = item
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.upcharges_list_frame, text=f"{item_name} ({item_price:.2f}$)", variable=var)
            cb.pack(anchor='w')
            self.upcharges_list_checkboxes.append(var)
            
    def refresh_textures_list(self):
        # Clear previous widgets in the frame
        for widget in self.textures_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT name, image FROM textures")
        textures = self.cursor.fetchall()

        self.textures = textures
        self.textures_list_checkboxes = []
        for index, item in enumerate(textures):
            item_name, item_image = item
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.textures_list_frame, text=item_name, variable=var)
            cb.pack(anchor='w')
            self.textures_list_checkboxes.append(var)

    def refresh_ticket_types_list(self):
        self.ticket_types_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT id, name FROM ticket_types")
        self.ticket_types = self.cursor.fetchall()

        for ticket_type in self.ticket_types:
            self.ticket_types_listbox.insert(tk.END, ticket_type[1])

    def add_selected_garment(self, event):
        selection = self.garments_listbox.curselection()
        if selection:
            index = selection[0]
            garment_id, garment_name, garment_image = self.garments[index]

            self.show_pricing_popup(garment_id, garment_name, garment_image)

    def show_pricing_popup(self, garment_id, garment_name, garment_image):
        pricing_window = tk.Toplevel(self)
        pricing_window.title("Set Prices for Garment Variations")

        ttk.Label(pricing_window, text=f"Set Prices for {garment_name}").grid(column=0, row=0, columnspan=2, padx=10, pady=10)

        image = Image.open(garment_image)
        image.thumbnail((50, 50))
        photo = ImageTk.PhotoImage(image)
        image_label = ttk.Label(pricing_window, image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection
        image_label.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

        # Price input for the original garment
        ttk.Label(pricing_window, text=f"{garment_name} Price").grid(column=0, row=2, padx=10, pady=5, sticky='w')
        original_price_var = tk.StringVar()
        ttk.Entry(pricing_window, textvariable=original_price_var).grid(column=1, row=2, padx=10, pady=5)

        price_vars = [(None, original_price_var)]  # Add the original garment price var to the list

        # Get garment variations from the database
        self.cursor.execute("SELECT id, name FROM variations WHERE garment_id = ?", (garment_id,))
        variations = self.cursor.fetchall()

        # Adjust row index for variations
        row = 3
        for variation_id, variation_name in variations:
            ttk.Label(pricing_window, text=variation_name).grid(column=0, row=row, padx=10, pady=5, sticky='w')
            price_var = tk.StringVar()
            ttk.Entry(pricing_window, textvariable=price_var).grid(column=1, row=row, padx=10, pady=5)
            price_vars.append((variation_id, price_var))
            row += 1

        def save_prices():
            # Save the price for the original garment
            original_price = original_price_var.get()
            self.cursor.execute('''
                INSERT OR REPLACE INTO garment_prices (garment_id, price)
                VALUES (?, ?)
            ''', (garment_id, original_price))
            
            for variation_id, price_var in price_vars[1:]:  # Skip the first item which is the original price
                price = price_var.get()
                # Save the price to the database or to the in-memory structure
                self.cursor.execute('''
                    INSERT OR REPLACE INTO variation_prices (variation_id, price)
                    VALUES (?, ?)
                ''', (variation_id, price))
            self.db_conn.commit()
            pricing_window.destroy()
            self.add_garment_to_list(garment_id, garment_name, garment_image, price_vars)

        ttk.Button(pricing_window, text="Save", command=save_prices).grid(column=0, row=row, padx=10, pady=10)
        ttk.Button(pricing_window, text="Cancel", command=pricing_window.destroy).grid(column=1, row=row, padx=10, pady=10)

    def add_garment_to_list(self, garment_id, garment_name, garment_image, price_vars):
        frame = tk.Frame(self.selected_garments_listbox)
        frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(frame, text=garment_name).pack(side=tk.LEFT, padx=5, pady=5)

        image = Image.open(garment_image)
        image.thumbnail((50, 50))
        photo = ImageTk.PhotoImage(image)
        tk.Label(frame, image=photo).pack(side=tk.LEFT, padx=5, pady=5)
        frame.image = photo  # Keep a reference to avoid garbage collection

        # Create a frame for the prices to control layout
        prices_frame = tk.Frame(frame)
        prices_frame.pack(side=tk.LEFT, padx=5, pady=5)

        # Store the garment and its prices
        prices = [f"{garment_name}: {price_vars[0][1].get()}"]
        self.cursor.execute("SELECT name FROM variations WHERE garment_id = ?", (garment_id,))
        variations = self.cursor.fetchall()

        for (variation_id, price_var), variation in zip(price_vars[1:], variations):
            prices.append(f"{variation[0]}: {price_var.get()}")

        # Display prices in a 3x3 grid
        for i, price in enumerate(prices):
            row = i // 3
            col = i % 3
            tk.Label(prices_frame, text=price, font=("TkDefaultFont", 8)).grid(row=row, column=col, padx=5, pady=5)

    def show_garment_context_menu(self, event):
        widget = event.widget
        index = widget.nearest(event.y)
        if index != -1:
            self.selected_garments_listbox.selection_clear(0, tk.END)
            self.selected_garments_listbox.selection_set(index)
            self.garment_context_menu.post(event.x_root, event.y_root)

    def remove_selected_garment(self):
        selection = self.selected_garments_listbox.curselection()
        if selection:
            self.selected_garments_listbox.delete(selection[0])

    def save_ticket_type(self):
        ticket_type = self.ticket_type_entry.get()
        if not ticket_type:
            messagebox.showerror("Error", "Please enter the ticket type name.")
            return

        selected_garments = [self.selected_garments_listbox.get(index) for index in range(self.selected_garments_listbox.size())]
        selected_colors = [color[0] for color, var in zip(self.colors, self.colors_list_checkboxes) if var.get()]
        selected_patterns = [pattern[0] for pattern, var in zip(self.patterns, self.patterns_list_checkboxes) if var.get()]
        selected_coupons_discounts = [item[0] for item, var in zip(self.coupons_discounts, self.coupons_discounts_list_checkboxes) if var.get()]
        selected_upcharges = [item[0] for item, var in zip(self.upcharges, self.upcharges_list_checkboxes) if var.get()]
        selected_textures = [item[0] for item, var in zip(self.textures, self.textures_list_checkboxes) if var.get()]

        self.cursor.execute('''
            INSERT INTO ticket_types (name, garments, colors, patterns, coupons_discounts, upcharges, textures)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_type, ','.join(selected_garments), ','.join(selected_colors), ','.join(selected_patterns), ','.join(selected_coupons_discounts), ','.join(selected_upcharges), ','.join(selected_textures)))

        self.db_conn.commit()
        messagebox.showinfo("Success", "Ticket Type saved successfully!")
        self.refresh_ticket_types_list()

    def edit_ticket_type(self, event=None):
        selection = self.ticket_types_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a ticket type to edit.")
            return

        index = selection[0]
        ticket_type_id, ticket_type_name = self.ticket_types[index]

        # Retrieve the ticket type details from the database
        self.cursor.execute('SELECT * FROM ticket_types WHERE id = ?', (ticket_type_id,))
        ticket_type = self.cursor.fetchone()

        self.ticket_type_entry.delete(0, tk.END)
        self.ticket_type_entry.insert(0, ticket_type[1])

        selected_garments = ticket_type[2].split(',')
        selected_colors = ticket_type[3].split(',')
        selected_patterns = ticket_type[4].split(',')
        selected_coupons_discounts = ticket_type[5].split(',')
        selected_upcharges = ticket_type[6].split(',')
        selected_textures = ticket_type[7].split(',')

        self.set_selected_items(self.selected_garments_listbox, self.garments, selected_garments)
        self.set_selected_checkboxes(self.colors_list_checkboxes, self.colors, selected_colors)
        self.set_selected_checkboxes(self.patterns_list_checkboxes, self.patterns, selected_patterns)
        self.set_selected_checkboxes(self.coupons_discounts_list_checkboxes, self.coupons_discounts, selected_coupons_discounts)
        self.set_selected_checkboxes(self.upcharges_list_checkboxes, self.upcharges, selected_upcharges)
        self.set_selected_checkboxes(self.textures_list_checkboxes, self.textures, selected_textures)

        self.save_button.config(text="Update Ticket Type", command=lambda: self.update_ticket_type(ticket_type_id))

    def set_selected_items(self, listbox, items, selected_items):
        listbox.delete(0, tk.END)
        for item in items:
            if item[1] in selected_items:
                listbox.insert(tk.END, item[1])

    def set_selected_checkboxes(self, checkboxes, items, selected_items):
        for var, item in zip(checkboxes, items):
            var.set(item[0] in selected_items)

    def update_ticket_type(self, ticket_type_id):
        ticket_type = self.ticket_type_entry.get()
        if not ticket_type:
            messagebox.showerror("Error", "Please enter the ticket type name.")
            return

        selected_garments = [self.selected_garments_listbox.get(index) for index in range(self.selected_garments_listbox.size())]
        selected_colors = [color[0] for color, var in zip(self.colors, self.colors_list_checkboxes) if var.get()]
        selected_patterns = [pattern[0] for pattern, var in zip(self.patterns, self.patterns_list_checkboxes) if var.get()]
        selected_coupons_discounts = [item[0] for item, var in zip(self.coupons_discounts, self.coupons_discounts_list_checkboxes) if var.get()]
        selected_upcharges = [item[0] for item, var in zip(self.upcharges, self.upcharges_list_checkboxes) if var.get()]
        selected_textures = [item[0] for item, var in zip(self.textures, self.textures_list_checkboxes) if var.get()]

        self.cursor.execute('''
            UPDATE ticket_types
            SET name = ?, garments = ?, colors = ?, patterns = ?, coupons_discounts = ?, upcharges = ?, textures = ?
            WHERE id = ?
        ''', (ticket_type, ','.join(selected_garments), ','.join(selected_colors), ','.join(selected_patterns), ','.join(selected_coupons_discounts), ','.join(selected_upcharges), ','.join(selected_textures), ticket_type_id))

        self.db_conn.commit()
        messagebox.showinfo("Success", "Ticket Type updated successfully!")
        self.save_button.config(text="Save Ticket Type", command=self.save_ticket_type)
        self.refresh_ticket_types_list()

    def delete_ticket_type(self):
        selection = self.ticket_types_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a ticket type to delete.")
            return

        index = selection[0]
        ticket_type_id, _ = self.ticket_types[index]

        self.cursor.execute('DELETE FROM ticket_types WHERE id = ?', (ticket_type_id,))
        self.db_conn.commit()
        self.refresh_ticket_types_list()

    def edit_selected_item(self):
        if self.ticket_types_listbox.curselection():
            self.edit_ticket_type()
        elif self.selected_garments_listbox.curselection():
            self.edit_selected_garment()

    def delete_selected_item(self):
        if self.ticket_types_listbox.curselection():
            self.delete_ticket_type()
        elif self.selected_garments_listbox.curselection():
            self.remove_selected_garment()

    def edit_selected_garment(self):
        selection = self.selected_garments_listbox.curselection()
        if selection:
            index = selection[0]
            garment_info = self.selected_garments_listbox.get(index)
            garment_name, prices_text = garment_info.split(" Prices: ")
            garment_id = self.get_garment_id_by_name(garment_name)

            self.cursor.execute("SELECT id, name FROM variations WHERE garment_id = ?", (garment_id,))
            variations = self.cursor.fetchall()

            # Split prices_text into original price and variations prices
            original_price, variations_prices = prices_text.split(", Variations: ")
            original_price = original_price.replace("Original: ", "")

            price_vars = [(None, tk.StringVar(value=original_price))]  # Include the original garment price

            pricing_window = tk.Toplevel(self)
            pricing_window.title("Edit Prices for Garment Variations")

            ttk.Label(pricing_window, text=f"Edit Prices for {garment_name}").grid(column=0, row=0, columnspan=2, padx=10, pady=10)

            image = Image.open(self.get_garment_image_by_id(garment_id))
            image.thumbnail((50, 50))
            photo = ImageTk.PhotoImage(image)
            image_label = ttk.Label(pricing_window, image=photo)
            image_label.image = photo  # Keep a reference to avoid garbage collection
            image_label.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

            # Add original garment price input
            ttk.Label(pricing_window, text=f"{garment_name} Price").grid(column=0, row=2, padx=10, pady=5, sticky='w')
            original_price_var = price_vars[0][1]
            ttk.Entry(pricing_window, textvariable=original_price_var).grid(column=1, row=2, padx=10, pady=5)

            row = 3
            for variation, price in zip(variations, variations_prices.split(", ")):
                variation_id, variation_name = variation
                ttk.Label(pricing_window, text=variation_name).grid(column=0, row=row, padx=10, pady=5, sticky='w')
                price_var = tk.StringVar(value=price)
                ttk.Entry(pricing_window, textvariable=price_var).grid(column=1, row=row, padx=10, pady=5)
                price_vars.append((variation_id, price_var))
                row += 1

            def save_prices():
                # Save the price for the original garment
                original_price = original_price_var.get()
                self.cursor.execute('''
                    INSERT OR REPLACE INTO garment_prices (garment_id, price)
                    VALUES (?, ?)
                ''', (garment_id, original_price))
                
                for variation_id, price_var in price_vars[1:]:  # Skip the first item which is the original price
                    price = price_var.get()
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO variation_prices (variation_id, price)
                        VALUES (?, ?)
                    ''', (variation_id, price))
                self.db_conn.commit()
                pricing_window.destroy()
                self.update_garment_in_list(index, garment_id, garment_name, price_vars)

            ttk.Button(pricing_window, text="Save", command=save_prices).grid(column=0, row=row, padx=10, pady=10)
            ttk.Button(pricing_window, text="Cancel", command=pricing_window.destroy).grid(column=1, row=row, padx=10, pady=10)

    def get_garment_id_by_name(self, garment_name):
        self.cursor.execute("SELECT id FROM garments WHERE name = ?", (garment_name,))
        return self.cursor.fetchone()[0]

    def get_garment_image_by_id(self, garment_id):
        self.cursor.execute("SELECT image FROM garments WHERE id = ?", (garment_id,))
        return self.cursor.fetchone()[0]

    def update_garment_in_list(self, index, garment_id, garment_name, price_vars):
        self.selected_garments_listbox.delete(index)
        self.add_garment_to_list(garment_id, garment_name, self.get_garment_image_by_id(garment_id), price_vars)


if __name__ == "__main__":
    db_conn = create_db_connection()
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = TicketTypeCreationWindow(root, db_conn)
    app.mainloop()
