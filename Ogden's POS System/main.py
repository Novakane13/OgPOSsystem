import tkinter as tk
from tkinter import Image, ttk
from tkinter import filedialog
from initialize_db import create_db_connection, initialize_db
from app.views.customer_search_window import CustomerSearchWindow
from app.views.customer_account_window import CustomerAccountWindow  # Import the new window

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POS System for Dry Cleaners")
        self.root.geometry("2000x1050")  # Set the size of the main window here
        self.db_conn = create_db_connection()
        self.create_widgets()
        self.create_menu()
        
    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Upload Image", command=self.upload_image)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        button_data = [
            ("Next Customer", self.open_search_window),
            ("Ticket Type Creation", self.open_ticket_type_creation_window),
            ("Delivery Route Creation", self.open_delivery_route_creation),
            ("Garment Creation", self.open_garment_creation),
            ("Design Specials", self.open_design_specials),
            ("Color List Creation", self.open_color_list_creation_window),
            ("Pattern List Creation", self.open_pattern_list_creation_window),
            ("Coupons and Discounts Creation", self.open_coupons_discounts_creation_window),
            ("Upcharges List Creation", self.open_upcharges_creation_window),
            ("Textures List Creation", self.open_textures_creation_window)
        ]

        for text, command in button_data:
            button = ttk.Button(buttons_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5, pady=5)
            
        # Frame for the image
        self.image_frame = ttk.Frame(self)
        self.image_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(side=tk.TOP, pady=10)

    def open_search_window(self):
        CustomerSearchWindow(self.root, self.db_conn)

    def open_ticket_type_creation_window(self):
        CustomerAccountWindow(self.root, self.db_conn)

    def open_delivery_route_creation(self):
        # Code to open the delivery route creation window
        pass

    def open_garment_creation(self):
        # Code to open the garment creation window
        pass

    def open_design_specials(self):
        # Code to open the design specials window
        pass

    def open_color_list_creation_window(self):
        # Code to open the color list creation window
        pass

    def open_pattern_list_creation_window(self):
        # Code to open the pattern list creation window
        pass

    def open_coupons_discounts_creation_window(self):
        # Code to open the coupons and discounts creation window
        pass

    def open_upcharges_creation_window(self):
        # Code to open the upcharges creation window
        pass

    def open_textures_creation_window(self):
        # Code to open the textures creation window
        pass
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            self.display_image(file_path)

    def display_image(self, file_path):
        image = Image.open(file_path)
        image = image.resize((self.image_frame.winfo_width(), self.image_frame.winfo_height()), Image.LANCZOS)
        self.photo = Image.tk.PhotoImage(image)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
