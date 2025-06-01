import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.user_role import UserRole
from utils.database import Session
from models.url_top_menu import UrlTopMenu
from models.url_sub_menu import UrlSubMenu
from models.business_role_content import BusinessRoleContent

class SetRolePermissionView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent
        
        # Dictionary to store checkbox variables with sub menu IDs
        self.checkbox_vars = {}
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Configure custom checkbutton style with larger font
        style.configure("Custom.TCheckbutton", 
                       font=("Helvetica", 12),
                       background="white")
        
        
        # Create form
        self.create_form()
    
    def select_all_checkboxes(self, value=True):
        """Select or deselect all checkboxes"""
        for var in self.checkbox_vars.values():
            var.set(value)

    def create_form(self):
        """Creates the role creation form."""
        # Title
        # ttk.Label(
        #     self,
        #     text="Create New Role",
        #     font=("Helvetica", 16, "bold"),
        #     bootstyle="primary"
        # ).pack(pady=(0, 20))
        
        roles = self.get_role_option_list()
            
        # Role selection
        ttk.Label(
            self,
            text="Role:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        
        # Store roles for later reference
        self.roles = roles
        # Create a dictionary to map role names to IDs
        self.role_name_to_id = {role.name: role.id for role in roles}
        
        # Extract role names for display
        role_names = [role.name for role in roles]
        
        role_var = ttk.StringVar()
        self.role_combobox = ttk.Combobox(
            self, 
            textvariable=role_var,
            values=role_names,
            state="readonly",
            bootstyle="primary"
        )
        # Bind the combobox selection event
        self.role_combobox.bind('<<ComboboxSelected>>', self.on_role_selected)
        self.role_combobox.pack(fill="x", pady=(0, 15))
        self.role_combobox.configure(width=50)
        
        # Set default selection to first role
        if role_names:
            self.role_combobox.set(role_names[0])

        # Add Select All / Deselect All buttons in a frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Select All",
            command=lambda: self.select_all_checkboxes(True),
            bootstyle="info-outline",
            width=15
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Deselect All",
            command=lambda: self.select_all_checkboxes(False),
            bootstyle="danger-outline",
            width=15
        ).pack(side="left", padx=5)

        top_menus = self.get_url_top_menu()

        # Create a canvas with scrollbar for the menu container
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill="both", expand=True, pady=(10, 20))
        
        # Create canvas
        canvas = ttk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        # Create a frame inside canvas to hold the menu items
        menu_container = ttk.Frame(canvas)
        
        # Configure the canvas
        menu_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window inside canvas
        canvas.create_window((0, 0), window=menu_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Calculate grid positions
        for index, top_menu in enumerate(top_menus):
            # Create a frame for each top menu and its sub-menus
            menu_frame = ttk.Frame(menu_container, padding=10)
            row = index // 3  # Integer division to determine row
            col = index % 3   # Modulo to determine column
            menu_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nw")

            # Menu Name
            ttk.Label(
                menu_frame,
                text=f"{top_menu.menu_name}:",
                font=("Helvetica", 14, "bold"),
                bootstyle="dark").pack(anchor="w", pady=(0, 5))
            
            # Sub Menu
            sub_menus = self.get_url_sub_menu(top_menu.id)
            for sub_menu in sub_menus:
                check_var = ttk.BooleanVar(value=False)
                # Store the checkbox variable with sub menu ID
                self.checkbox_vars[sub_menu.id] = check_var
                ttk.Checkbutton(
                    menu_frame,
                    text=f"{sub_menu.sub_menu_name}",
                    variable=check_var,
                    bootstyle="primary",
                    style='Custom.TCheckbutton').pack(anchor="w", pady=2)

        # Configure grid columns to be evenly spaced
        menu_container.grid_columnconfigure(0, weight=1)
        menu_container.grid_columnconfigure(1, weight=1)
        menu_container.grid_columnconfigure(2, weight=1)
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Submit button
        ttk.Button(
            self,
            text="Set Permission",
            command=self.save_permissions,
            bootstyle="primary",
            width=20
        ).pack(pady=10)

    def get_role_option_list(self):
        """Get option list from database."""
        session = Session()
        options = session.query(UserRole).all()
        session.close()
        return options
    
    # Url SUb Menu2
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
            print("somerhing goes wrong!")
        
    def get_url_sub_menu(self,id):
        try:
            print("dynamic menu called")
            session = Session()
            # top_menu = session.query(UrlTopMenu).all()
            # print(f"top menu: {top_menu}")

            menu_top = session.query(UrlSubMenu).filter_by(top_menu_id=id).all()
            session.close()
            return menu_top
            
        except Exception:
            print("somerhing goes wrong!")
    
    def on_role_selected(self, event):
        """Handle role selection change"""
        selected_role_name = self.role_combobox.get()
        selected_role_id = self.role_name_to_id[selected_role_name]
        
        # Reset all checkboxes first
        self.select_all_checkboxes(False)
        
        try:
            # Load existing permissions for the selected role
            session = Session()
            existing_permissions = session.query(BusinessRoleContent).filter_by(user_role_id=selected_role_id).all()
            
            # Set checkboxes based on existing permissions
            for permission in existing_permissions:
                if permission.sub_menu_id in self.checkbox_vars:
                    self.checkbox_vars[permission.sub_menu_id].set(True)
            
            session.close()
            
        except Exception as e:
            print(f"Error loading permissions: {str(e)}")
            session.close()

    def save_permissions(self):
        """Save the selected permissions"""
        selected_role_name = self.role_combobox.get()
        # Get the role ID using the mapping
        selected_role_id = self.role_name_to_id[selected_role_name]
        selected_permissions = []
        
        # Get only checked permissions
        for sub_menu_id, var in self.checkbox_vars.items():
            if var.get():
                selected_permissions.append(sub_menu_id)
        
        try:
            # print(f"Role Name: {selected_role_name}")
            # print(f"Role ID: {selected_role_id}")
            # print(f"Selected Permissions IDs: {selected_permissions}")

            session = Session()
            # Delete existing permissions for this role
            session.query(BusinessRoleContent).filter_by(user_role_id=selected_role_id).delete()
            
            # Add new permissions
            for sub_menu_id in selected_permissions:
                session.add(BusinessRoleContent(
                    user_role_id=selected_role_id,
                    sub_menu_id=sub_menu_id
                ))
            session.commit()
            session.close()
            self.select_all_checkboxes(False)
            
            ttk.dialogs.Messagebox.show_info(
                message="Permissions updated successfully!",
                title="Success",
                parent=self
            )
            
        except Exception as e:
            session.rollback()
            session.close()
            ttk.dialogs.Messagebox.show_error(
                message=f"Error updating permissions: {str(e)}",
                title="Error",
                parent=self
            )
