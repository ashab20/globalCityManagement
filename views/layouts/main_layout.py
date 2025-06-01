import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils.window_manager import WindowManager


class MainLayout(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create window manager for internal windows
        self.window_manager = WindowManager(self)
        self.window_manager.windows_frame.pack(fill="both", expand=True)
    
    def create_menu_bar(self):
        """Creates the menu bar."""
        menu_bar = ttk.Frame(self, bootstyle="primary")
        menu_bar.pack(fill="x", side="top")
        
        # User Management
        user_frame = ttk.Frame(menu_bar, bootstyle="primary")
        user_frame.pack(side="left", padx=10)
        
        ttk.Label(
            user_frame,
            text="User Management",
            bootstyle="inverse-primary",
            font=("Helvetica", 10, "bold")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            user_frame,
            text="Create User",
            command=self.show_create_user,
            bootstyle="primary-outline",
            width=12
        ).pack(side="left", padx=2)
        
        ttk.Button(
            user_frame,
            text="List Users",
            command=self.show_list_users,
            bootstyle="primary-outline",
            width=12
        ).pack(side="left", padx=2)
        
        # ttk.Button(
        #     user_frame,
        #     text="Create Role",
        #     command=self.show_create_role,
        #     bootstyle="primary-outline",
        #     width=12
        # ).pack(side="left", padx=2)
        
        # Shop Management
        shop_frame = ttk.Frame(menu_bar, bootstyle="primary")
        shop_frame.pack(side="left", padx=10)
        
        ttk.Label(
            shop_frame,
            text="Shop Management",
            bootstyle="inverse-primary",
            font=("Helvetica", 10, "bold")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            shop_frame,
            text="Create Shop",
            command=self.show_create_shop,
            bootstyle="primary-outline",
            width=12
        ).pack(side="left", padx=2)
        
        ttk.Button(
            shop_frame,
            text="List Shops",
            command=self.show_list_shops,
            bootstyle="primary-outline",
            width=12
        ).pack(side="left", padx=2)
        
        # Logout button on the right
        ttk.Button(
            menu_bar,
            text="Logout",
            command=self.logout,
            bootstyle="danger-outline",
            width=10
        ).pack(side="right", padx=10)
    
    def show_create_user(self):
        self.master.show_create_user()
    
    def show_list_users(self):
        self.master.show_list_users()
    
    def show_create_role(self):
        self.master.show_create_role()
    
    def show_create_shop(self):
        self.master.show_create_shop()
    
    def show_list_shops(self):
        self.master.show_list_shops()
    
    def logout(self):
        self.master.logout()
