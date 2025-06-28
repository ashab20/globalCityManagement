import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Menu
from utils.window_manager import WindowManager
from views.accounting.shop_renter_due_report import ShopRenterDueReportView
from views.unit.create_unit import CreateUnitView
from views.unit.unit_list import UnitListView
from views.users.create_user_view import CreateUserView
from views.users.list_user_view import ListUserView
from views.users.create_role_view import CreateRoleView
from views.users.list_role_view import ListRoleView
from views.shops.create_shop_view import CreateShopView
from views.shops.list_shop_view import ListShopView
from views.shopOwner.create_shop_owner_view import CreateShopOwnerView
from views.shopOwner.lisr_shop_owner_view import ListShopOwnerView
from views.shopRenters.create_renter_view import CreateShopRenterView
from views.shopRenters.list_renter_view import ShopRenterListView
from views.shopAllocation.create_shop_allocation_view import CreateShopAllocationView
from views.shopAllocation.list_shop_allocation_view import ListShopAllocationView
from views.bankAccount.create_bank_account_view import CreateBankAccountView
from views.bankAccount.list_bank_account_view import ListBankAccountView
from views.journalVoucher.create_journal_voucher import CreateJournalVoucherView
from views.journalVoucher.list_journal_voucher_view import ListJournalVoucherView
from views.utilities.utilities_list import ListOfUtilitySettingsView
from views.utilities.list_utilities_view import ListUtilitiesView
from views.utilities.create_utilities import CreateUtilitySettingView
from views.role_permission.set_role_permission import SetRolePermissionView
from views.role_permission.role_permission_list import RolePermissionDetails
from views.billInfo.create_bill import CreateBillInfoView
from views.billInfo.bill_info_list import BillInfoListView
from PIL import Image, ImageTk
import os
from models.role_permissions import RolePermission
from models.user import User
from utils.database import Session
from models.url_top_menu import UrlTopMenu
from models.url_sub_menu import UrlSubMenu
from views.billInfo.create_particular import CreateParticularView
from views.billInfo.particular_list import ParticularListView
from views.accounting.trial_balance import TrialBalanceView
from views.accounting.ledger_balance import LedgerBalanceView
from views.accounting.balance_sheet import BalanceSheetView
from views.accounting.profit_loss import ProfitLossView
from views.billCollection.create_bill_collection import CreateBillCollectionView
from controllers.accounting_controller import AccountingController
from views.billCollection.bill_collection_list import CollectionListView
from views.accounting.shop_owner_due_report import ShopOwnerDueReportView
from views.accounting.shop_renter_due_report import ShopRenterDueReportView
from views.category.create_category import CreateCategoryView
from views.category.category_list import CategoryListView
from views.product.create_product import CreateProductView
from views.product.product_list import ProductListView
from utils.toltip import ToolTip
# from sqlalchemy.orm import Session


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

        # Render internal menu
        self.render_internal_menu(self.container)
    
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
        
        # Get user role and permissions
        user_role = self.get_user_role()
        user_permissions = self.get_user_permissions(user_role)
        # print(f"User role: {user_role} , Permissions: {user_permissions}")
       

    #   Dynamic Menu
        menus = self.get_url_top_menu()
        # print(menus)
        for mt in menus:
            print(mt.menu_name)
            topMenu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label=mt.menu_name, menu=topMenu)
            submenus = self.get_url_sub_menu(mt.id)
            for sub in submenus:
                try:
                    # Convert command name to lowercase and replace spaces with underscores
                    method_name = sub.command_name.lower().replace(' ', '_')
                    menu_action = getattr(self, method_name)
                    topMenu.add_command(label=sub.sub_menu_name, command=menu_action)
                except AttributeError:
                    print(f"Warning: Method {method_name} not found for menu item {sub.sub_menu_name}")
                    continue
       
    
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
            # print(f"Role Permission for {role}: {role_permission}")
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
    
    def get_url_top_menu(self):
        try:
            print("dynamic menu called")
            session = Session()
            # top_menu = session.query(UrlTopMenu).all()
            # print(f"top menu: {top_menu}")

            menu_top = session.query(UrlTopMenu).order_by(UrlTopMenu.menu_order).all() 
            session.close()
            return menu_top
            
        except Exception:
            print("somerhing goes worn!")
        
    def get_url_sub_menu(self,id):
        try:
            print("dynamic menu called")
            session = Session()
            # top_menu = session.query(UrlTopMenu).all()
            # print(f"top menu: {top_menu}")

            menu_top = session.query(UrlSubMenu).filter_by(top_menu_id=id).order_by(UrlSubMenu.sub_menu_order).all()
            session.close()
            return menu_top
            
        except Exception:
            print("somerhing goes wrong!")
    

    ICON_MAP = {
        'Users': 'users.png',
        'Shop': 'shop.png',
        'Reports': 'reports.png',
        'Account': 'account.png',
        'Help': 'help.png',
        'Profile': 'profile.png',
        'Utility': 'utility.png'
        # Add more mappings as needed
    }

    def show_welcome(self):
        """Shows welcome message and dashboard-style top menus."""
        welcome_frame = ttk.Frame(self.container, style="TFrame")
        welcome_frame.pack(pady=30, fill='both', expand=True)

        # Show logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'logo.png')
        logo_image = Image.open(logo_path).resize((300, 100), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        
        ttk.Label(welcome_frame, image=self.logo_photo, style="TLabel").pack(pady=(0, 20))

        # Dashboard menu box container
        dashboard_frame = ttk.Frame(welcome_frame)
        dashboard_frame.pack()

        try:
            top_menus = self.get_url_top_menu()

            for i, mt in enumerate(top_menus):
                # Box per top menu
                menu_box = ttk.LabelFrame(
                    dashboard_frame,
                    text=mt.menu_name,
                    padding=10,
                    style="TLabelframe"
                )
                menu_box.grid(row=i // 3, column=i % 3, padx=20, pady=15, sticky="nsew")

                # Try to load icon for menu (optional)
                icon_path = os.path.join('assets', 'icons', mt.icon or '')
                if os.path.exists(icon_path):
                    icon_image = Image.open(icon_path).resize((40, 40), Image.Resampling.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    icon_label = ttk.Label(menu_box, image=icon_photo)
                    icon_label.image = icon_photo  # keep a reference
                    icon_label.pack(pady=(0, 5))

                # Submenus as buttons
                submenus = self.get_url_sub_menu(mt.id)
                for sub in submenus:
                    try:
                        method_name = sub.command_name.lower().replace(' ', '_')
                        menu_action = getattr(self, method_name)
                        ttk.Button(menu_box, text=sub.sub_menu_name, command=menu_action).pack(pady=2, fill='x')
                    except AttributeError:
                        print(f"Method {method_name} not found for submenu {sub.sub_menu_name}")
        except Exception as e:
            print(f"Failed to show dashboard menus: {e}")


    # def show_welcome(self):
    #     """Shows welcome message."""
    #     welcome_frame = ttk.Frame(self.container, style="TFrame")
    #     welcome_frame.pack(pady=50)
        
    #     # Load and display logo
    #     logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'logo.png')
    #     logo_image = Image.open(logo_path)
    #     # Resize logo to 300x100
    #     logo_image = logo_image.resize((300, 100), Image.Resampling.LANCZOS)
    #     self.logo_photo = ImageTk.PhotoImage(logo_image)
        
    #     ttk.Label(
    #         welcome_frame,
    #         image=self.logo_photo,
    #         style="TLabel"
    #     ).pack(pady=(0, 30))
        
    #     ttk.Label(
    #         welcome_frame,
    #         text="Use the menu above to manage users and shops",
    #         font=("Helvetica", 12),
    #         bootstyle="secondary"
    #     ).pack()
    

    # !MENU FUNTIONS START

    def create_user(self):
        """Opens create user window."""
        self.window_manager.create_window("Create User", CreateUserView)
    
    def list_users(self):
        """Opens list users window."""
        self.window_manager.create_window("User List", ListUserView)
    
    def create_role(self):
        """Opens create role window."""
        self.window_manager.create_window("New Role Form", CreateRoleView)

    def role_list(self):
        """Opens create role window."""
        self.window_manager.create_window("Role List", ListRoleView)

    def user_role_permission(self):
        """Opens create role window."""
        self.window_manager.create_window("Set User Role Permission", SetRolePermissionView)

    def user_role_permission_details(self):
        """Opens create role window."""
        self.window_manager.create_window("User Role Permission Details", RolePermissionDetails)



    # !SHOP FUNTIONS START
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
    
    # !BANK ACCOUNT FUNTIONS START
    def create_bank_account(self):
        """Opens list shop allocations window."""
        self.window_manager.create_window("New Bank Account Form", CreateBankAccountView)

    def on_logout(self):
        """Logs out the user."""
        print("logout called")
        self.window_manager.create_window("Login", LoginView)
    
    def list_bank_accounts(self):
        """Opens list bank accounts window."""
        self.window_manager.create_window("Bank Account List", ListBankAccountView)
        print("list bank accounts called")
        
    def create_journal_voucher(self):
        """Opens create journal voucher window."""
        self.window_manager.create_window("Create Journal Voucher", CreateJournalVoucherView)
        print("create journal voucher called")

    def list_journal_vouchers(self):
        """Opens list journal vouchers window."""
        self.window_manager.create_window("List Journal Vouchers", ListJournalVoucherView)
        print("list journal vouchers called")

    # !UTILITIES FUNTIONS START
    def create_utilities(self):
        """Opens Create Utility Setting window."""
        self.window_manager.create_window("Create Utility Setting", CreateUtilitySettingView)
        # print("list journal vouchers called")

    def list_utilities(self):
        """Opens list of utility settings window."""
        self.window_manager.create_window("Utilities List", ListUtilitiesView)
        # print("list journal vouchers called")

    def create_particular(self):
        """Opens create particular window."""
        self.window_manager.create_window("Create Particular", CreateParticularView)
        # print("list journal vouchers called")

    def list_particular(self):
        """Opens list of particular window."""
        self.window_manager.create_window("List Particular", ParticularListView)
        # print("list journal vouchers called")

    def password_change_form(self):
        """Opens list journal vouchers window."""
        # self.window_manager.create_window("List Journal Vouchers", ListJournalVouchersView)
        print("list journal vouchers called")

    def show_about(self):
        """Shows about dialog."""
        ttk.dialogs.Messagebox.show_info(
            title="About",
            message="Global City Management System\nVersion 1.0\n\nDeveloped by BITPOINT TECHNOLOGIES LTD.",
            parent=self
        )



    # BILL INFO FUNTIONS START

    def create_bill_info(self):
        """Opens create bill info window."""
        self.window_manager.create_window("Create Bill Info", CreateBillInfoView)
    
    def list_bill_info(self):
        """Opens list bill info window."""
        self.window_manager.create_window("List Bill Info", BillInfoListView)

    # def create_bill_particular(self):
    #     """Opens create bill particular window."""
    #     self.window_manager.create_window("Create Bill Particular", CreateBillParticularView)
    
    # def list_bill_particular(self):
    #     """Opens list bill particular window."""
    #     self.window_manager.create_window("List Bill Particular", BillParticularListView)


    # !INVENTORY FUNTIONS START

    def product_category(self):
        """Opens create product category window."""
        self.window_manager.create_window("Product Category", CreateCategoryView)

    def product_category_list(self):
        """Opens list product category window."""
        self.window_manager.create_window("Product Category List", CategoryListView)

    def create_product(self):
        """Opens list bill info window."""
        self.window_manager.create_window("Product List", CreateProductView)

    def product_details_list(self):
        """Opens list bill info window."""
        self.window_manager.create_window("Product List", ProductListView)

    def demand_product(self):
        """Opens Demand Product window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def demand_product_list(self):
        """Opens Demand Product List window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def create_unit(self):
        """Opens Create Unit window."""
        self.window_manager.create_window("Create Unit", CreateUnitView)

    def unit_list(self):
        """Opens Unit List window."""
        self.window_manager.create_window("Unit List", UnitListView)

    def product_purchase(self):
        """Opens Product Purchase window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def product_purchase_list(self):
        """Opens Product Purchase List window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def product_issues(self):
        """Opens Product Issues window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def product_issues_list(self):
        """Opens Product Issues List window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)
    
    
    
    # !ACCOUNTING FUNTIONS START

    def stock_report(self):
        """Opens Stock Report window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def stock_report_list(self):
        """Opens Stock Report List window."""
        # self.window_manager.create_window("List Bill Info", BillInfoListView)

    def trial_balance(self):
        """Opens trial balance window."""
        self.window_manager.create_window("Trial Balance", TrialBalanceView)
    
    def ledger_balance(self):
        """Opens ledger balance window."""
        self.window_manager.create_window("Ledger Balance", LedgerBalanceView)

    def balance_sheet(self):
        """Opens balance sheet window."""
        self.window_manager.create_window("Balance Sheet", BalanceSheetView)
    
    def shop_owner_due_report(self):
        """Opens due report window."""
        self.window_manager.create_window("Shop Owner Due Report", ShopOwnerDueReportView)

    def shop_renter_due_report(self):
        """Opens due report window."""
        self.window_manager.create_window("Shop Renter Due Report", ShopRenterDueReportView)

    
    def profit_loss(self):
        """Opens profit loss window."""
        self.window_manager.create_window("Profit Loss", ProfitLossView)
    
    def bill_collection(self):
        """Opens bill collection window."""
        self.window_manager.create_window("Bill Collection", CreateBillCollectionView)

    def bill_collection_list(self):
        """Opens bill collection window."""
        self.window_manager.create_window("Bill Collection List", CollectionListView)
    

    # *MENU FUNTIONS END

    def dynamicMenu(self):
        # dynamic menu
        print("dynamic menu called")
        session = session()
        menu_top = session.query(UrlTopMenu).order_by(UrlTopMenu.menu_order).all()
        for mt in menu_top:
            print(mt.menu_name)

    # Enhanced icon handling
    ICON_MAP = {
        'Users': '👤',
        'Shop': '🏪',
        'Reports': '📊',
        'Account': '💰',
        'Help': '❓',
        'Profile': '👤',
        'Utility': '⚙️',
        'User Management': '👥',
        'Shop Management': '🏬',
        'Accounting': '📈',
        'Billing': '🧾',
        'Inventory': '📦',
        'Settings': '⚙️',
        'Logout': '🚪'
    }

    def render_internal_menu(self, parent_frame):
        """
        Renders icon-only internal menu at the top of the window.
        """
        try:
            top_menus = self.get_url_top_menu()
            
            # Create dedicated menu bar frame
            menu_bar = ttk.Frame(parent_frame, height=40, style="Primary.TFrame")
            menu_bar.pack(fill="x", pady=(0, 10))
            menu_bar.pack_propagate(False)  # Keep fixed height
            
            # Add application logo on left
            logo_frame = ttk.Frame(menu_bar, width=150)
            logo_frame.pack(side="left", fill="y")
            
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'assets', 'images', 'logo.png')
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path).resize((120, 30), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(logo_img)
                ttk.Label(logo_frame, image=self.logo).pack(padx=10, pady=5)
            
            # Menu container
            menu_container = ttk.Frame(menu_bar)
            menu_container.pack(side="left", fill="both", expand=True, padx=20)
            
            for mt in top_menus:
                # Get icon from mapping or use default
                icon_char = self.ICON_MAP.get(mt.menu_name.strip(), '📋')
                
                # Create menu button
                btn = ttk.Button(
                    menu_container,
                    text=icon_char,
                    command=lambda m=mt: self.open_first_submenu(m),
                    width=3,
                    bootstyle="light-outline"
                )
                btn.pack(side="left", padx=5)
                ToolTip(btn, text=mt.menu_name, delay=500)
                
            # Add logout button on right
            logout_btn = ttk.Button(
                menu_bar,
                text="🚪",
                command=self.on_logout,
                width=3,
                bootstyle="danger-outline"
            )
            logout_btn.pack(side="right", padx=10)
            ToolTip(logout_btn, text="Logout", delay=500)
            
        except Exception as e:
            print(f"Error rendering internal menu: {e}")
    
    def open_first_submenu(self, top_menu):
        submenus = self.get_url_sub_menu(top_menu.id)
        if not submenus:
            return

        first_sub = submenus[0]
        try:
            method_name = first_sub.command_name.lower().replace(' ', '_')
            menu_action = getattr(self, method_name)
            menu_action()
        except AttributeError:
            print(f"No method: {method_name}")


