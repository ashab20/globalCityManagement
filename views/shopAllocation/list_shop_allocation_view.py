import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_allocation import ShopAllocation
from models.shop_profile import ShopProfile
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session
from views.shopAllocation.create_shop_allocation_view import CreateShopAllocationView


class ListShopAllocationView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent

        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Create shop allocation list
        self.create_allocation_list()

    def create_allocation_list(self):
        """Creates the shop allocation list view."""
        # Create treeview
        columns = (
            "ID", 
            "Shop Name", 
            "Shop Floor", 
            "Shop Number", 
            "Renter Name", 
            "Renter Phone", 
            "From Year", 
            "From Month", 
            "To Year", 
            "To Month", 
            "Status"
        )
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_allocation)
        self.context_menu.add_command(label="Delete", command=self.delete_allocation)

        # Bind right-click to show context menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.edit_allocation)

        # Load shop allocations
        self.load_shop_allocations()

        # Add buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_shop_allocations,
            bootstyle="primary-outline",
            width=10
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Add New",
            command=self.add_new_allocation,
            bootstyle="success-outline",
            width=10
        ).pack(side="left", padx=5)

    def show_context_menu(self, event):
        """Show context menu for right-click"""
        # Select the row under the cursor
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)

    def add_new_allocation(self):
        """Open a window to add a new shop allocation"""
        edit_window = tk.Toplevel(self)
        edit_window.title("Add New Shop Allocation")
        edit_window.geometry("600x500")

        create_allocation_view = CreateShopAllocationView(edit_window)
        create_allocation_view.pack(fill="both", expand=True)

        # Update save button to close window after saving
        create_allocation_view.submit_button.configure(
            command=lambda: (create_allocation_view.save_shop_allocation(), edit_window.destroy(), self.load_shop_allocations())
        )

    def edit_allocation(self, event=None):
        """Edit the selected shop allocation"""
        selected_item = self.tree.selection()
        if not selected_item:
            ttk.dialogs.Messagebox.show_warning(
                message="Please select an allocation to edit.", 
                title="No Selection", 
                parent=self
            )
            return

        # Get the allocation ID from the selected row
        allocation_id = self.tree.item(selected_item[0])['values'][0]

        try:
            session = Session()
            existing_allocation = session.query(ShopAllocation).filter_by(id=allocation_id).first()
            session.close()

            if not existing_allocation:
                raise ValueError("Allocation not found")

            edit_window = tk.Toplevel(self)
            edit_window.title("Edit Shop Allocation")
            edit_window.geometry("600x500")

            create_allocation_view = CreateShopAllocationView(edit_window, existing_allocation)
            create_allocation_view.pack(fill="both", expand=True)

            # Update save button to close window after saving
            create_allocation_view.submit_button.configure(
                command=lambda: (create_allocation_view.save_shop_allocation(), edit_window.destroy(), self.load_shop_allocations())
            )

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error editing allocation: {str(e)}", 
                title="Error", 
                parent=self
            )

    def delete_allocation(self):
        """Delete the selected shop allocation"""
        selected_item = self.tree.selection()
        if not selected_item:
            ttk.dialogs.Messagebox.show_warning(
                message="Please select an allocation to delete.", 
                title="No Selection", 
                parent=self
            )
            return

        # Confirm deletion
        confirm = ttk.dialogs.Messagebox.show_question(
            message="Are you sure you want to delete this allocation?", 
            title="Confirm Deletion", 
            parent=self
        )

        if not confirm:
            return

        # Get the allocation ID from the selected row
        allocation_id = self.tree.item(selected_item[0])['values'][0]

        try:
            session = Session()
            allocation = session.query(ShopAllocation).filter_by(id=allocation_id).first()
            
            if not allocation:
                raise ValueError("Allocation not found")

            session.delete(allocation)
            session.commit()
            session.close()

            # Refresh the list
            self.load_shop_allocations()

            ttk.dialogs.Messagebox.show_info(
                message="Shop allocation deleted successfully!", 
                title="Success", 
                parent=self
            )

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error deleting allocation: {str(e)}", 
                title="Error", 
                parent=self
            )

    def load_shop_allocations(self):
        """Load shop allocations from the database with relational data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            
            # Join with shop and renter profiles to get their details
            allocations = session.query(
                ShopAllocation, 
                ShopProfile, 
                ShopRenterProfile
            ).join(
                ShopProfile, 
                ShopAllocation.shop_profile_id == ShopProfile.id
            ).join(
                ShopRenterProfile, 
                ShopAllocation.renter_profile_id == ShopRenterProfile.id
            ).all()

            for allocation, shop, renter in allocations:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        allocation.id,
                        shop.shop_name,  # Shop Name
                        shop.floor_no,   # Shop Floor
                        shop.shop_no,    # Shop Number
                        renter.renter_name,  # Renter Name
                        renter.phone,    # Renter Phone
                        allocation.from_year,
                        allocation.from_month,
                        allocation.to_year,
                        allocation.to_month,
                        "Active" if allocation.close_status == 0 else "Closed"
                    )
                )

            session.close()

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading shop allocations: {str(e)}",
                title="Error",
                parent=self
            )
