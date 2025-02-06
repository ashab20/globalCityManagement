import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.shop_profile import ShopProfile
from models.shop_owner_profile import ShopOwnerProfile
from utils.database import Session
from views.shops.create_shop_view import CreateShopView
import tkinter as tk


class ListShopView(ttk.Frame):
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
        
        # Create shop list
        self.create_shop_list()
    
    def create_shop_list(self):
        """Creates the shop list view."""
        # Create treeview
        columns = (
            "ID", 
            "Shop Name", 
            "Shop Number", 
            "Floor Number", 
            "Shop Size", 
            "Rent Amount", 
            "Shop Type", 
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

        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_shop)

        # Add context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_shop)
        self.context_menu.add_command(label="Delete", command=self.delete_shop)

        # Bind right-click to show context menu
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Load shops
        self.load_shops()

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(10, 0))

        # Refresh button
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_shops,
            bootstyle="primary-outline",
            width=10
        ).pack(side="left", padx=5)

        # Add New button
        ttk.Button(
            button_frame,
            text="Add New",
            command=self.add_new_shop,
            bootstyle="success-outline",
            width=10
        ).pack(side="left", padx=5)

        # Edit button
        self.edit_button = ttk.Button(
            button_frame,
            text="Edit",
            command=self.edit_shop,
            bootstyle="warning-outline",
            width=10
        )
        self.edit_button.pack(side="left", padx=5)

        # Delete button
        self.delete_button = ttk.Button(
            button_frame,
            text="Delete",
            command=self.delete_shop,
            bootstyle="danger-outline",
            width=10
        )
        self.delete_button.pack(side="left", padx=5)

    def show_context_menu(self, event):
        """Show context menu for right-click"""
        # Select the row under the cursor
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_shop(self, event=None):
        """Edit the selected shop"""
        selected_item = self.tree.selection()
        if not selected_item:
            ttk.dialogs.Messagebox.show_warning(
                message="Please select a shop to edit.", 
                title="No Selection", 
                parent=self
            )
            return

        # Get the shop ID from the selected row
        shop_id = self.tree.item(selected_item[0])['values'][0]

        try:
            session = Session()
            existing_shop = session.query(ShopProfile).filter_by(id=shop_id).first()
            session.close()

            if not existing_shop:
                raise ValueError("Shop not found")

            edit_window = tk.Toplevel(self)
            edit_window.title("Edit Shop")
            edit_window.geometry("600x500")

            create_shop_view = CreateShopView(edit_window, existing_shop)
            create_shop_view.pack(fill="both", expand=True)

            # Update save button to close window after saving
            create_shop_view.save_button.configure(
                command=lambda: (create_shop_view.create_shop(), edit_window.destroy(), self.load_shops())
            )

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error editing shop: {str(e)}", 
                title="Error", 
                parent=self
            )

    def delete_shop(self):
        """Delete the selected shop"""
        selected_item = self.tree.selection()
        if not selected_item:
            ttk.dialogs.Messagebox.show_warning(
                message="Please select a shop to delete.", 
                title="No Selection", 
                parent=self
            )
            return

        # Confirm deletion
        confirm = ttk.dialogs.Messagebox.show_question(
            message="Are you sure you want to delete this shop?", 
            title="Confirm Deletion", 
            parent=self
        )

        if not confirm:
            return

        # Get the shop ID from the selected row
        shop_id = self.tree.item(selected_item[0])['values'][0]

        try:
            session = Session()
            shop = session.query(ShopProfile).filter_by(id=shop_id).first()
            
            if not shop:
                raise ValueError("Shop not found")

            session.delete(shop)
            session.commit()
            session.close()

            # Refresh the list
            self.load_shops()

            ttk.dialogs.Messagebox.show_info(
                message="Shop deleted successfully!", 
                title="Success", 
                parent=self
            )

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error deleting shop: {str(e)}", 
                title="Error", 
                parent=self
            )

    def add_new_shop(self):
        """Open a window to add a new shop"""
        edit_window = tk.Toplevel(self)
        edit_window.title("Add New Shop")
        edit_window.geometry("600x500")

        create_shop_view = CreateShopView(edit_window)
        create_shop_view.pack(fill="both", expand=True)

        # Update save button to close window after saving
        create_shop_view.save_button.configure(
            command=lambda: (create_shop_view.create_shop(), edit_window.destroy(), self.load_shops())
        )

    def load_shops(self):
        """Load shops from database and populate Treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            shops = session.query(ShopProfile).all()

            for shop in shops:
                item = self.tree.insert(
                    "",
                    "end",
                    values=(
                        shop.id,
                        shop.shop_name,
                        shop.floor_no,
                        shop.shop_no,
                        shop.descreption,
                        shop.rent_amout,
                        shop.shop_type,
                        shop.status
                    )
                )
                self.tree.item(item, tags=(shop.id,))  # Store shop ID in tag

            session.close()

            # Bind click events
            self.tree.bind("<Button-1>", self.on_item_click)
            self.tree.bind("<Double-1>", self.on_item_double_click)

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading shops: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_double_click(self, event):
        """Open CreateShopView with data when clicking on Edit."""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            shop_id = item_values[0]  # Extract shop ID

            session = Session()
            shop = session.query(ShopProfile).filter_by(id=shop_id).first()
            session.close()

        if shop:
            self.edit_shop(shop)

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        # Get the column clicked
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        
        if row and column:
            # Get the shop ID from the row's tag
            shop_id = self.tree.item(row, "tags")[0]
            
            # Get the column number (returns '#1', '#2', etc.)
            col_num = int(column.replace('#', ''))
            
            # Check if Edit or Delete column was clicked
            if col_num == 7:  # Delete column
                self.delete_shop_by_id(shop_id)
            elif col_num == 6:  # Edit column
                session = Session()
                shop = session.query(ShopProfile).filter_by(id=shop_id).first()
                session.close()
                
                if shop:
                    self.edit_shop(shop)

    def delete_shop_by_id(self, shop_id):
        """Delete shop by ID with confirmation."""
        try:
            session = Session()
            shop_to_delete = session.query(ShopProfile).filter_by(id=shop_id).first()
            
            if shop_to_delete:
                # Show confirmation dialog
                result = ttk.dialogs.Messagebox.show_question(
                    message=f"Are you sure you want to delete shop '{shop_to_delete.shop_name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )
                
                if result == "Yes":
                    session.delete(shop_to_delete)
                    session.commit()
                    
                    # Refresh shop list
                    self.load_shops()
                    
                    ttk.dialogs.Messagebox.show_info(
                        message="Shop deleted successfully!",
                        title="Success",
                        parent=self
                    )
            
            session.close()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error deleting shop: {str(e)}",
                title="Error",
                parent=self
            )

    def delete_shop(self, shop):
        """Delete shop from database with confirmation."""
        # Show confirmation dialog
        result = ttk.dialogs.Messagebox.show_question(
            message=f"Are you sure you want to delete shop '{shop.shop_name}'?",
            title="Confirm Delete",
            parent=self,
            buttons=["Yes:primary", "No:secondary"]
        )
        
        if result == "Yes":
            try:
                session = Session()
                shop_to_delete = session.query(ShopProfile).filter_by(id=shop.id).first()
                
                if shop_to_delete:
                    session.delete(shop_to_delete)
                    session.commit()
                    
                    # Refresh shop list
                    self.load_shops()
                    
                    ttk.dialogs.Messagebox.show_info(
                        message="Shop deleted successfully!",
                        title="Success",
                        parent=self
                    )
                
                session.close()
            except Exception as e:
                ttk.dialogs.Messagebox.show_error(
                    message=f"Error deleting shop: {str(e)}",
                    title="Error",
                    parent=self
                )
