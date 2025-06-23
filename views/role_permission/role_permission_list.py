import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session
from views.shopRenters.create_renter_view import CreateShopRenterView
from models.user_role import UserRole
from models.business_role_content import BusinessRoleContent
from models.url_sub_menu import UrlSubMenu
from models.url_top_menu import UrlTopMenu


class RolePermissionDetails(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_list()

    def create_list(self):
        # Create the Treeview widget with show="tree headings" to show hierarchy
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=("Role Name", "Active Status", "Actions"),
            show="tree headings",
            selectmode="browse"
        )

        # Configure the columns
        self.tree.heading("#0", text="Permissions")  # Tree column for hierarchy
        self.tree.heading("Role Name", text="Role Name")
        self.tree.heading("Active Status", text="Active Status")
        self.tree.heading("Actions", text="Actions")

        self.tree.column("#0", width=450, stretch=True)  # Tree column
        self.tree.column("Role Name", width=150, stretch=True)
        self.tree.column("Active Status", width=100, stretch=False)
        self.tree.column("Actions", width=150, stretch=False)

        # Configure style
        style = ttk.Style()
        style.configure("Treeview", indent=20)  # Indent for hierarchy levels

        # Add scrollbars
        yscrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=yscrollbar.set)

        xscrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview,
            bootstyle="primary-round"
        )
        self.tree.configure(xscrollcommand=xscrollbar.set)

        # Pack widgets
        self.tree.pack(side="top", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar.pack(side="bottom", fill="x")

        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Load the role permissions
        self.load_role_permissions()

    def load_role_permissions(self):
        """Loads the role permissions from the database and displays them in the Treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            roles = session.query(UserRole).all()

            for role in roles:
                # Insert role as main item
                role_item = self.tree.insert(
                    "",
                    "end",
                    text="",  # No text in tree column for role
                    values=(
                        role.name,
                        "Active",
                        "Edit | Delete"
                    )
                )

                # Get permissions for this role
                permissions = session.query(BusinessRoleContent).filter_by(user_role_id=role.id).all()
                top_menu_dict = {}  # Dictionary to organize by top menu

                # Group permissions by top menu
                for perm in permissions:
                    sub_menu = session.query(UrlSubMenu).filter_by(id=perm.sub_menu_id).first()
                    if sub_menu:
                        top_menu = session.query(UrlTopMenu).filter_by(id=sub_menu.top_menu_id).first()
                        if top_menu:
                            if top_menu.id not in top_menu_dict:
                                top_menu_dict[top_menu.id] = {
                                    'name': top_menu.menu_name,
                                    'sub_menus': []
                                }
                            top_menu_dict[top_menu.id]['sub_menus'].append(sub_menu.sub_menu_name)

                # Insert top menus and their sub-menus
                for top_menu_id, menu_data in top_menu_dict.items():
                    # Insert top menu
                    top_menu_item = self.tree.insert(
                        role_item,
                        "end",
                        text=menu_data['name'],
                        values=("", "", "")
                    )

                    # Insert sub-menus
                    for sub_menu_name in menu_data['sub_menus']:
                        self.tree.insert(
                            top_menu_item,
                            "end",
                            text=f"✓ {sub_menu_name}",
                            values=("", "", "")
                        )

            session.close()

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading role permissions: {str(e)}",
                title="Error",
                parent=self
            )

    def on_double_click(self, event):
        """Handle double-click event to edit renter."""
        item = self.tree.identify_row(event.y)
        if item:
            # Get the renter details
            values = self.tree.item(item, "values")
            renter_id = values[0]
            
            # Fetch the full renter details
            try:
                session = Session()
                renter = session.query(ShopRenterProfile).filter_by(id=renter_id).first()
                session.close()
                
                if renter:
                    self.edit_renter(renter)
            except Exception as e:
                ttk.dialogs.Messagebox.show_error(
                    message=f"Error fetching renter details: {str(e)}",
                    title="Error",
                    parent=self
                )

    def edit_renter(self, renter):
        """Open edit renter dialog."""
        edit_window = ttk.Toplevel(title="Edit Shop Renter")
        edit_window.geometry("600x700")
        
        # Create CreateShopRenterView with existing renter
        create_renter_view = CreateShopRenterView(edit_window, renter)
        create_renter_view.pack(fill="both", expand=True)
        
        # Update save button to close window after saving
        create_renter_view.submit_button.configure(
            command=lambda: (create_renter_view.save_shop_renter(), edit_window.destroy(), self.load_role_permissions())
        )

    def delete_renter(self):
        """Delete renter from the database with confirmation."""
        # Get the selected item
        selected_item = self.tree.selection()
        if not selected_item:
            ttk.dialogs.Messagebox.show_warning(
                message="Please select a renter to delete.",
                title="Warning",
                parent=self
            )
            return

        # Confirm deletion
        result = ttk.dialogs.Messagebox.show_question(
            message="Are you sure you want to delete this renter?",
            title="Confirm Deletion",
            parent=self,
            buttons=["Yes:primary", "No"]
        )

        if result == "Yes":
            try:
                # Get renter ID from selected row
                values = self.tree.item(selected_item[0], "values")
                renter_id = values[0]

                # Delete the renter
                session = Session()
                renter = session.query(ShopRenterProfile).filter_by(id=renter_id).first()
                
                if renter:
                    session.delete(renter)
                    session.commit()
                    session.close()

                    # Reload the list
                    self.load_role_permissions()
                    
                    ttk.dialogs.Messagebox.show_info(
                        message="Shop renter deleted successfully!",
                        title="Success",
                        parent=self
                    )
                else:
                    ttk.dialogs.Messagebox.show_error(
                        message="Renter not found.",
                        title="Error",
                        parent=self
                    )

            except Exception as e:
                ttk.dialogs.Messagebox.show_error(
                    message=f"Error deleting renter: {str(e)}",
                    title="Error",
                    parent=self
                )

    def create_context_menu(self):
        """Create context menu for right-click actions."""
        context_menu = ttk.Menu(self, tearoff=0)
        context_menu.add_command(label="Edit", command=lambda: self.edit_renter(self.get_selected_renter()))
        context_menu.add_command(label="Delete", command=self.delete_renter)
        return context_menu

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select the row under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            # Show context menu
            context_menu = self.create_context_menu()
            context_menu.post(event.x_root, event.y_root)

    def get_selected_renter(self):
        """Get the selected renter."""
        selected_item = self.tree.selection()
        if not selected_item:
            return None

        values = self.tree.item(selected_item[0], "values")
        renter_id = values[0]

        try:
            session = Session()
            renter = session.query(ShopRenterProfile).filter_by(id=renter_id).first()
            session.close()
            return renter
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error fetching renter details: {str(e)}",
                title="Error",
                parent=self
            )
            return None
