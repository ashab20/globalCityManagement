import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Menu
from utils.window_manager import WindowManager
from views.users.create_user_view import CreateUserView
from views.users.list_user_view import ListUserView
from views.users.create_role_view import CreateRoleView
from views.shops.create_shop_view import CreateShopView
from views.shops.list_shop_view import ListShopView
from views.shopOwner.create_shop_owner_view import CreateShopOwnerView
from views.shopOwner.lisr_shop_owner_view import ListShopOwnerView
from views.shopRenters.create_renter_view import CreateShopRenterView
from views.shopRenters.list_renter_view import ShopRenterListView
from views.shopAllocation.create_shop_allocation_view import CreateShopAllocationView
from views.shopAllocation.list_shop_allocation_view import ListShopAllocationView
from PIL import Image, ImageTk
import os


class DashboardView(ttk.Frame):
    def __init__(self, parent, on_logout=None):
        super().__init__(parent)
        self.parent = parent
        self.on_logout = on_logout
        
        # Create main container
        self.container = ttk.Frame(self, style="TFrame")
        self.container.pack(fill="both", expand=True)
        
        # Create window manager
        self.window_manager = WindowManager(self.container)
        
        # Create menu bar
        self.create_menu()
        
        # Show welcome message
        self.show_welcome()
    
    def create_menu(self):
        """Creates the main menu bar."""
        # Configure menu colors
        self.parent.option_add('*Menu.background', '#f8f9fa')
        self.parent.option_add('*Menu.foreground', '#212529')
        self.parent.option_add('*Menu.selectColor', '#4361ee')
        self.parent.option_add('*Menu.activeBorderWidth', 0)
        self.parent.option_add('*Menu.borderWidth', 0)
        self.parent.option_add('*Menu.relief', 'flat')
        self.parent.option_add('*Menu.activeBackground', '#e9ecef')
        self.parent.option_add('*Menu.activeForeground', '#212529')
        
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # User Management Menu
        user_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="User Management", menu=user_menu)
        user_menu.add_command(label="Create User", command=self.create_user)
        user_menu.add_command(label="List Users", command=self.list_users)
        user_menu.add_separator()
        user_menu.add_command(label="Create Role", command=self.create_role)
        
        # Shop Management Menu
        shop_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Shop Management", menu=shop_menu)
        shop_menu.add_command(label="Create Shop", command=self.create_shop)
        shop_menu.add_command(label="List Shops", command=self.list_shops)
        user_menu.add_separator()
        shop_menu.add_command(label="Create Shop Owner", command=self.create_shop_owner)
        shop_menu.add_command(label="List Shop Owners", command=self.list_shop_owners)
        user_menu.add_separator()
        shop_menu.add_command(label="Create Shop Renter", command=self.create_shop_renter)
        shop_menu.add_command(label="List Shop Renters", command=self.list_shop_renters)
        user_menu.add_separator()
        shop_menu.add_command(label="Create Shop Allocation", command=self.create_shop_allocation)
        shop_menu.add_command(label="List Shop Allocations", command=self.list_shop_allocations)
        
        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Logout Menu (right-aligned)
        menubar.add_command(label="Logout", command=self.on_logout)
    
    def show_welcome(self):
        """Shows welcome message."""
        welcome_frame = ttk.Frame(self.container, style="TFrame")
        welcome_frame.pack(pady=50)
        
        # Load and display logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'logo.png')
        logo_image = Image.open(logo_path)
        # Resize logo to 300x100
        logo_image = logo_image.resize((300, 100), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        
        ttk.Label(
            welcome_frame,
            image=self.logo_photo,
            style="TLabel"
        ).pack(pady=(0, 30))
        
        ttk.Label(
            welcome_frame,
            text="Use the menu above to manage users and shops",
            font=("Helvetica", 12),
            bootstyle="secondary"
        ).pack()
    
    def create_user(self):
        """Opens create user window."""
        self.window_manager.create_window("Create User", CreateUserView)
    
    def list_users(self):
        """Opens list users window."""
        self.window_manager.create_window("User List", ListUserView)
    
    def create_role(self):
        """Opens create role window."""
        self.window_manager.create_window("Create Role", CreateRoleView)
    
    def create_shop(self):
        """Opens create shop window."""
        self.window_manager.create_window("Create Shop", CreateShopView)
    
    def list_shops(self):
        """Opens list shops window."""
        self.window_manager.create_window("Shop List", ListShopView)

    def create_shop_owner(self):
        """Opens create shop owner window."""
        self.window_manager.create_window("Create Shop Owner", CreateShopOwnerView)
    
    def list_shop_owners(self):
        """Opens list shop owners window."""
        self.window_manager.create_window("Shop Owner List", ListShopOwnerView)

    def create_shop_renter(self):
        """Opens create shop renter window."""
        self.window_manager.create_window("Create Shop Renter", CreateShopRenterView)
    
    def list_shop_renters(self):
        """Opens list shop renters window."""
        self.window_manager.create_window("Shop Renter List", ShopRenterListView)

    def create_shop_allocation(self):
        """Opens create shop allocation window."""
        self.window_manager.create_window("Create Shop Allocation", CreateShopAllocationView)
    
    def list_shop_allocations(self):
        """Opens list shop allocations window."""
        self.window_manager.create_window("Shop Allocation List", ListShopAllocationView)

    
    def show_about(self):
        """Shows about dialog."""
        ttk.dialogs.Messagebox.show_info(
            title="About",
            message="Global City Management System\nVersion 1.0\n\nDeveloped by Your Name",
            parent=self
        )
