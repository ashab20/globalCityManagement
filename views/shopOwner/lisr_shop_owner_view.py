import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.shop_owner_profile import ShopOwnerProfile
from utils.database import Session
from views.shopOwner.create_shop_owner_view import CreateShopOwnerView


class ListShopOwnerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Create shop owner list
        self.create_owner_list()

    def create_owner_list(self):
        """Creates the shop owner list view."""
        # Create treeview
        columns = ("ID", "Name", "Phone", "Email", "Address", "NID Number", "Status", "Edit", "Delete")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Owner Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        self.tree.heading("NID Number", text="NID Number")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("Phone", width=120, anchor="w")
        self.tree.column("Email", width=150, anchor="w")
        self.tree.column("Address", width=200, anchor="w")
        self.tree.column("NID Number", width=100, anchor="center")
        self.tree.column("Status", width=80, anchor="center")
        self.tree.column("Edit", width=75, anchor="center")
        self.tree.column("Delete", width=75, anchor="center")

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

        # Load shop owners
        self.load_shop_owners()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_shop_owners,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def load_shop_owners(self):
        """Load shop owners from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            owners = session.query(ShopOwnerProfile).all()

            for owner in owners:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        owner.id,
                        owner.ownner_name,
                        owner.phone,
                        owner.email,
                        owner.address,
                        owner.nid_number,
                        "Active" if owner.active_status == 1 else "Inactive",
                        "Edit",
                        "Delete"
                    ),
                    tags=(owner.id,)  # Store owner ID in tag
                )

            session.close()

        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading shop owners: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        # Get the column clicked
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        
        if row and column:
            # Get the owner ID from the row's tag
            owner_id = self.tree.item(row, "tags")[0]
            
            # Get the column number (returns '#1', '#2', etc.)
            col_num = int(column.replace('#', ''))
            
            # Check if Edit or Delete column was clicked
            if col_num == 9:  # Delete column
                self.delete_shop_owner_by_id(owner_id)
            elif col_num == 8:  # Edit column
                session = Session()
                owner = session.query(ShopOwnerProfile).filter_by(id=owner_id).first()
                session.close()
                
                if owner:
                    self.edit_shop_owner(owner)

    def on_item_double_click(self, event):
        """Open CreateShopOwnerView with data when double-clicking."""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            owner_id = item_values[0]  # Extract owner ID

            session = Session()
            owner = session.query(ShopOwnerProfile).filter_by(id=owner_id).first()
            session.close()

            if owner:
                self.edit_shop_owner(owner)

    def edit_shop_owner(self, shop_owner):
        """Open edit shop owner dialog."""
        edit_window = ttk.Toplevel(title="Edit Shop Owner")
        edit_window.geometry("600x700")
        
        # Create CreateShopOwnerView with existing shop owner
        create_shop_owner_view = CreateShopOwnerView(edit_window, shop_owner)
        create_shop_owner_view.pack(fill="both", expand=True)
        
        # Update save button to close window after saving
        create_shop_owner_view.submit_button.configure(
            command=lambda: (create_shop_owner_view.save_shop_owner(), edit_window.destroy(), self.load_shop_owners())
        )

    def update_shop_owner(self, existing_owner, create_shop_owner_view, edit_window):
        """Update existing shop owner details."""
        try:
            session = Session()
            owner_to_update = session.query(ShopOwnerProfile).filter_by(id=existing_owner.id).first()
            
            if not owner_to_update:
                Messagebox.show_error(message="Shop owner not found!", title="Error", parent=create_shop_owner_view)
                return
            
            # Validate and get values from form
            name = create_shop_owner_view.name_entry.get().strip()
            phone = create_shop_owner_view.phone_entry.get().strip()
            email = create_shop_owner_view.email_entry.get().strip()
            address = create_shop_owner_view.address_entry.get().strip()
            nid_number = create_shop_owner_view.nid_number_entry.get().strip()
            status = create_shop_owner_view.status_combobox.get().strip()
            
            # Validation checks
            if not all([name, phone, email, address, nid_number, status]):
                Messagebox.show_error(message="All fields are required!", title="Validation Error", parent=create_shop_owner_view)
                return
            
            # Update owner details
            owner_to_update.ownner_name = name
            owner_to_update.phone = phone
            owner_to_update.email = email
            owner_to_update.address = address
            owner_to_update.nid_number = nid_number
            owner_to_update.active_status = 1 if status == "Active" else 0
            
            session.commit()
            session.close()
            
            # Close edit window and refresh list
            edit_window.destroy()
            self.load_shop_owners()
            
            Messagebox.show_info(message="Shop owner updated successfully!", title="Success", parent=self)
        
        except Exception as e:
            Messagebox.show_error(message=f"Error updating shop owner: {str(e)}", title="Error", parent=create_shop_owner_view)

    def delete_shop_owner_by_id(self, owner_id):
        """Delete shop owner by ID with confirmation."""
        try:
            session = Session()
            owner_to_delete = session.query(ShopOwnerProfile).filter_by(id=owner_id).first()
            
            if owner_to_delete:
                # Show confirmation dialog
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete shop owner '{owner_to_delete.ownner_name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )
                
                if result == "Yes":
                    session.delete(owner_to_delete)
                    session.commit()
                    
                    # Refresh shop owner list
                    self.load_shop_owners()
                    
                    Messagebox.show_info(
                        message="Shop owner deleted successfully!",
                        title="Success",
                        parent=self
                    )
            
            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting shop owner: {str(e)}",
                title="Error",
                parent=self
            )
