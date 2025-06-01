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
from models.role_permissions import RolePermission
from models.user import User
from utils.database import Session


class DashboardView(ttk.Frame):
    def __init__(self, parent, current_user=None, on_logout=None):
        super().__init__(parent)
        self.parent = parent
        self.on_logout = on_logout
        self.current_user = current_user
        
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
        """Creates the main menu bar with role-based access control."""
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

        # Get the function by name and call it
        method_name = "get_top_menu"
        top_menu = getattr(self, method_name)()
        
        # Get user role and permissions
        user_role = self.get_user_role()
        user_permissions = self.get_user_permissions(user_role)
        print(f"User role: {user_role} , Permissions: {user_permissions}")

        # User Management Menu
        if user_permissions.get('user_management'):
            user_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="User Management", menu=user_menu)
            
            if 'create' in user_permissions['user_management']:
                user_menu.add_command(label="Create User", command=self.create_user)
            
            if 'read' in user_permissions['user_management']:
                user_menu.add_command(label="List Users", command=self.list_users)
        
        # Shop Management Menu
        if user_permissions.get('shop_management'):
            shop_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Shop Management", menu=shop_menu)
            
            # Shop Submenu
            if 'create' in user_permissions['shop_management']:
                shop_menu.add_command(label="Create Shop", command=self.create_shop)
            
            if 'read' in user_permissions['shop_management']:
                shop_menu.add_command(label="List Shops", command=self.list_shops)
            
            # Shop Owner Submenu
            if 'create' in user_permissions.get('shop_owner_management', []):
                shop_menu.add_command(label="Create Shop Owner", command=self.create_shop_owner)
            
            if 'read' in user_permissions.get('shop_owner_management', []):
                shop_menu.add_command(label="List Shop Owners", command=self.list_shop_owners)
            
            # Shop Renter Submenu
            if 'create' in user_permissions.get('shop_renter_management', []):
                shop_menu.add_command(label="Create Shop Renter", command=self.create_shop_renter)
            
            if 'read' in user_permissions.get('shop_renter_management', []):
                shop_menu.add_command(label="List Shop Renters", command=self.list_shop_renters)
            
            # Shop Allocation Submenu
            if 'create' in user_permissions.get('shop_allocation_management', []):
                shop_menu.add_command(label="Create Shop Allocation", command=self.create_shop_allocation)
            
            if 'read' in user_permissions.get('shop_allocation_management', []):
                shop_menu.add_command(label="List Shop Allocations", command=self.list_shop_allocations)
        
        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Logout Menu (right-aligned)
        menubar.add_command(label="Logout", command=self.on_logout)
    
    def get_user_role(self):
        """
        Retrieve the user's role from the database.
        
        :return: Role name as a string, default to 'User' if not found
        """
        if not self.current_user:
            return 'User'
        
        try:
            session = Session()
            user = session.query(User).filter_by(id=self.current_user.id).first()
            role = user.get_role_name() if user else 'User'
            session.close()
            return role
        except Exception:
            return 'User'
    
    def get_user_permissions(self, role):
        """
        Retrieve permissions for the given role.
        
        :param role: Role name
        :return: Dictionary of permissions
        """
        try:
            session = Session()
            role_permission = session.query(RolePermission).filter_by(role_name=role).first()
            
            if not role_permission:
                # If no role permission found, use default
                default_permissions = RolePermission.get_default_permissions()
                permissions = default_permissions.get(role, default_permissions['User'])
            else:
                permissions = role_permission.permissions
            
            session.close()
            return permissions
        except Exception:
            # Fallback to User permissions
            default_permissions = RolePermission.get_default_permissions()
            return default_permissions['User']
    
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
            message="Global City Management System\nVersion 1.0\n\nDeveloped by BITPOINT TECHNOLOGIES LTD.",
            parent=self
        )

    def get_top_menu(self):
        """Returns the top menu for the current user."""
        return "Create User"
