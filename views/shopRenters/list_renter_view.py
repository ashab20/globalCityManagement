import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session
from views.shopRenters.create_renter_view import CreateShopRenterView


class ShopRenterListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_list()

    def create_list(self):
        # Define the columns for Treeview
        columns = ("ID", "Renter Name", "Email", "Phone", "Active Status", "Actions")
        
        # Create the Treeview widget
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure the columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Renter Name", text="Renter Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Active Status", text="Active Status")
        self.tree.heading("Actions", text="Actions")

        self.tree.column("ID", width=50)
        self.tree.column("Renter Name", width=150)
        self.tree.column("Email", width=150)
        self.tree.column("Phone", width=120)
        self.tree.column("Active Status", width=100)
        self.tree.column("Actions", width=150)

        # Add vertical scrollbar
        yscrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=yscrollbar.set)

        # Add horizontal scrollbar
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

        # Bind double-click event for editing
        self.tree.bind("<Double-1>", self.on_double_click)

        # Load the renters from the database
        self.load_renters()

        # Bind right-click event for context menu
        self.tree.bind("<Button-3>", self.show_context_menu)


    def load_renters(self):
        """Loads the shop renters from the database and displays them in the Treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            renters = session.query(ShopRenterProfile).all()

            for renter in renters:
                active_status = "Active" if renter.active_status == 1 else "Inactive"
                # Insert renter data into the Treeview
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        renter.id,
                        renter.renter_name,
                        renter.email,
                        renter.phone,
                        active_status,
                        "Edit | Delete"
                    )
                )

            session.close()

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading shop renters: {str(e)}",
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
            command=lambda: (create_renter_view.save_shop_renter(), edit_window.destroy(), self.load_renters())
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
                    self.load_renters()
                    
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
