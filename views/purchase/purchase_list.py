import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from utils.database import Session
from models.product_purchase import ProductPurchase
from models.shop_profile import ShopProfile
from models.purchase_details import PurchaseDetails
from models.product import Product
from views.purchase.purchase_view import PurchaseShowView
from datetime import datetime

class PurchaseListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.pack(fill="both", expand=True)
        
        # Pagination variables
        self.current_page = 1
        self.page_size = 10
        self.total_records = 0
        
        # Create styles
        self.create_styles()
        
        # Create UI
        self.create_purchase_list()
        
        # Load initial data
        self.load_shops()
        self.load_purchases()

    def create_styles(self):
        """Create custom styles for the list view"""
        style = ttk.Style()
        
        # Header style
        style.configure("Header.TLabel", 
                        background="#4361ee", 
                        foreground="white", 
                        font=("Helvetica", 10, "bold"),
                        padding=5)
        
        style.configure("Treeview", background="#f8f9fa", fieldbackground="#f8f9fa")
        style.configure("Treeview.Heading", background="#4361ee", foreground="white")
        
        # Approved status style
        style.configure("Approved.TLabel", 
                        background="#28a745", 
                        foreground="white", 
                        font=("Helvetica", 9))
        
        # Pending status style
        style.configure("Pending.TLabel", 
                        background="#ffc107", 
                        foreground="black", 
                        font=("Helvetica", 9))
        
        # Rejected status style
        style.configure("Rejected.TLabel", 
                        background="#dc3545", 
                        foreground="white", 
                        font=("Helvetica", 9))

    def create_purchase_list(self):
        """Create the purchase list interface"""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            title_frame, 
            text="PURCHASE LIST", 
            font=("Helvetica", 16, "bold"), 
            bootstyle="inverse-primary",
            anchor="center"
        ).pack(fill="x", pady=5)
        
        # Filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Shop filter
        ttk.Label(filter_frame, text="Shop:", bootstyle="primary").grid(row=0, column=0, padx=2, sticky="e")
        self.shop_var = ttk.StringVar()
        self.shop_cb = ttk.Combobox(filter_frame, textvariable=self.shop_var, state="readonly", width=10)
        self.shop_cb.grid(row=0, column=1, padx=5, sticky="w")
        
        # Status filter
        ttk.Label(filter_frame, text="Status:", bootstyle="primary").grid(row=0, column=2, padx=2, sticky="e")
        self.status_var = ttk.StringVar(value="All")
        status_cb = ttk.Combobox(
            filter_frame, 
            textvariable=self.status_var, 
            values=["All", "Pending", "Approved", "Rejected"],
            state="readonly", 
            width=10
        )
        status_cb.grid(row=0, column=3, padx=5, sticky="w")
        
        # Date range filter
        ttk.Label(filter_frame, text="From:", bootstyle="primary").grid(row=0, column=4, padx=2, sticky="e")
        self.from_date = ttk.DateEntry(filter_frame, dateformat="%Y-%m-%d", width=10)
        self.from_date.grid(row=0, column=5, padx=5, sticky="w")
        
        ttk.Label(filter_frame, text="To:", bootstyle="primary").grid(row=0, column=6, padx=2, sticky="e")
        self.to_date = ttk.DateEntry(filter_frame, dateformat="%Y-%m-%d", width=10)
        self.to_date.grid(row=0, column=7, padx=5, sticky="w")
        
        # Filter button row (centered below the filters)
        filter_button_frame = ttk.Frame(self)
        filter_button_frame.pack(fill="x", pady=(0, 10))
        
        # Apply filter button centered
        filter_btn = ttk.Button(
            filter_button_frame, 
            text="Apply Filters", 
            command=self.load_purchases,
            bootstyle="primary-outline",
            width=15
        )
        filter_btn.pack(anchor="center", pady=5)
        
        # Treeview frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)
        
        # Create Treeview
        columns = (
            "id", "shop", "date", "subtotal", "discount", "grand_total", 
            "status"
        )
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=8,
            bootstyle="primary",
            selectmode="browse"  # Single selection mode
        )
        
        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("shop", text="Shop")
        self.tree.heading("date", text="Date")
        self.tree.heading("subtotal", text="Subtotal")
        self.tree.heading("discount", text="Discount")
        self.tree.heading("grand_total", text="Grand Total")
        self.tree.heading("status", text="Status")
        
        # Set column widths
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("shop", width=10, anchor="w")
        self.tree.column("date", width=20, anchor="center")
        self.tree.column("subtotal", width=10, anchor="e")
        self.tree.column("discount", width=10, anchor="e")
        self.tree.column("grand_total", width=20, anchor="e")
        self.tree.column("status", width=20, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, 
            orient="vertical", 
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click event for viewing details
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Action buttons frame (below the treeview)
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=10)
        
        # View button
        self.view_btn = ttk.Button(
            action_frame, 
            text="View Details", 
            command=self.view_selected,
            bootstyle="info",
            width=15,
            state="disabled"  # Disabled until selection
        )
        self.view_btn.pack(side="left", padx=10)
        
        # Approve button
        self.approve_btn = ttk.Button(
            action_frame, 
            text="Approve", 
            command=self.approve_selected,
            bootstyle="success",
            width=15,
            state="disabled"  # Disabled until selection
        )
        self.approve_btn.pack(side="left", padx=10)
        
        # Delete button
        self.delete_btn = ttk.Button(
            action_frame, 
            text="Delete", 
            command=self.delete_selected,
            bootstyle="danger",
            width=15,
            state="disabled"  # Disabled until selection
        )
        self.delete_btn.pack(side="left", padx=10)
        
        # Refresh button
        refresh_btn = ttk.Button(
            action_frame, 
            text="Refresh", 
            command=self.load_purchases,
            bootstyle="secondary",
            width=15
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Pagination frame
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(fill="x", pady=(0, 10))
        
        # First page button
        self.first_btn = ttk.Button(
            pagination_frame, 
            text="<< First", 
            command=lambda: self.change_page(1),
            bootstyle="primary-outline",
            width=10
        )
        self.first_btn.pack(side="left", padx=5)
        
        # Previous page button
        self.prev_btn = ttk.Button(
            pagination_frame, 
            text="< Previous", 
            command=self.prev_page,
            bootstyle="primary-outline",
            width=10
        )
        self.prev_btn.pack(side="left", padx=5)
        
        # Page info label
        self.page_label = ttk.Label(
            pagination_frame, 
            text="Page 1 of 1", 
            bootstyle="primary",
            width=15
        )
        self.page_label.pack(side="left", padx=10)
        
        # Next page button
        self.next_btn = ttk.Button(
            pagination_frame, 
            text="Next >", 
            command=self.next_page,
            bootstyle="primary-outline",
            width=10
        )
        self.next_btn.pack(side="left", padx=5)
        
        # Last page button
        self.last_btn = ttk.Button(
            pagination_frame, 
            text="Last >>", 
            command=self.last_page,
            bootstyle="primary-outline",
            width=10
        )
        self.last_btn.pack(side="left", padx=5)
        
        # Bind selection event to enable/disable buttons
        self.tree.bind("<<TreeviewSelect>>", self.on_selection_change)

    def load_shops(self):
        """Load shops into the filter combobox"""
        try:
            session = Session()
            shops = session.query(ShopProfile).all()
            session.close()
            
            shop_names = [f"{s.shop_name} (ID: {s.id})" for s in shops]
            shop_names.insert(0, "All Shops")
            self.shop_cb["values"] = shop_names
            self.shop_cb.current(0)
            
        except Exception as e:
            Messagebox.show_error(f"Error loading shops: {str(e)}", "Error", parent=self)

    def load_purchases(self):
        """Load purchases from the database with filters"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            session = Session()
            
            # Build query
            query = session.query(ProductPurchase).join(ShopProfile)
            
            # Apply shop filter
            selected_shop = self.shop_var.get()
            if selected_shop and selected_shop != "All Shops":
                shop_id = selected_shop.split("(ID: ")[1].rstrip(")")
                query = query.filter(ProductPurchase.shop_id == shop_id)
            
            # Apply status filter
            selected_status = self.status_var.get()
            if selected_status != "All":
                query = query.filter(ProductPurchase.status == selected_status)
            
            # Apply date range filter
            from_date = self.from_date.entry.get()
            to_date = self.to_date.entry.get()
            
            if from_date:
                query = query.filter(ProductPurchase.purchase_date >= from_date)
            if to_date:
                query = query.filter(ProductPurchase.purchase_date <= to_date)
            
            # Get total count for pagination
            self.total_records = query.count()
            total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
            
            # Apply pagination
            offset = (self.current_page - 1) * self.page_size
            purchases = query.order_by(ProductPurchase.purchase_date.desc()) \
                            .offset(offset) \
                            .limit(self.page_size) \
                            .all()
            
            # Populate treeview
            for purchase in purchases:
                shop = purchase.shop
                shop_name = f"{shop.shop_name} (ID: {shop.id})" if shop else "N/A"
                
                status_style = ""
                if purchase.status == "Approved":
                    status_style = "Approved.TLabel"
                elif purchase.status == "Rejected":
                    status_style = "Rejected.TLabel"
                else:
                    status_style = "Pending.TLabel"
                
                self.tree.insert(
                    "", 
                    "end", 
                    values=(
                        purchase.id,
                        shop_name,
                        purchase.purchase_date.strftime("%Y-%m-%d"),
                        f"₹{purchase.sub_total:.2f}",
                        f"₹{purchase.discount:.2f}",
                        f"₹{purchase.grand_total:.2f}",
                        purchase.status
                    ),
                    tags=(purchase.id, status_style)
                )
                
            session.close()
            
            # Apply tags for status styling
            for item in self.tree.get_children():
                tags = self.tree.item(item, "tags")
                if tags and len(tags) > 1:
                    self.tree.item(item, tags=tags)
            
            # Update pagination controls
            self.update_pagination_controls(total_pages)
            
        except Exception as e:
            Messagebox.show_error(f"Error loading purchases: {str(e)}", "Error", parent=self)
    
    def update_pagination_controls(self, total_pages):
        """Update pagination buttons and label"""
        # Update page label
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")
        
        # Update button states
        self.first_btn.config(state="normal" if self.current_page > 1 else "disabled")
        self.prev_btn.config(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < total_pages else "disabled")
        self.last_btn.config(state="normal" if self.current_page < total_pages else "disabled")
    
    def change_page(self, page):
        """Change to a specific page"""
        if page != self.current_page:
            self.current_page = page
            self.load_purchases()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.change_page(self.current_page - 1)
    
    def next_page(self):
        """Go to next page"""
        # Calculate total pages
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.change_page(self.current_page + 1)
    
    def last_page(self):
        """Go to last page"""
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.change_page(total_pages)
    
    def on_selection_change(self, event):
        """Handle selection change in treeview"""
        selected = self.tree.selection()
        if selected:
            # Enable action buttons when a row is selected
            self.view_btn.config(state="normal")
            self.approve_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            # Disable buttons when no row is selected
            self.view_btn.config(state="disabled")
            self.approve_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
    
    def get_selected_purchase_id(self):
        """Get ID of selected purchase"""
        selected = self.tree.selection()
        if selected:
            tags = self.tree.item(selected[0], "tags")
            if tags:
                return tags[0]
        return None
    
    def on_double_click(self, event):
        """Handle double-click event on treeview"""
        selected = self.tree.selection()
        if selected:
            purchase_id = self.get_selected_purchase_id()
            if purchase_id:
                self.view_purchase_details(purchase_id)
    
    def view_selected(self):
        """View selected purchase"""
        purchase_id = self.get_selected_purchase_id()
        if purchase_id:
            self.view_purchase_details(purchase_id)
    
    def approve_selected(self):
        """Approve selected purchase"""
        purchase_id = self.get_selected_purchase_id()
        if purchase_id:
            selected = self.tree.selection()
            self.approve_purchase(purchase_id, selected[0])
    
    def delete_selected(self):
        """Delete selected purchase"""
        purchase_id = self.get_selected_purchase_id()
        if purchase_id:
            selected = self.tree.selection()
            self.delete_purchase(purchase_id, selected[0])
    
    def view_purchase_details(self, purchase_id):
        """Open detail view for selected purchase"""
        detail_window = ttk.Toplevel(self)
        detail_window.title(f"Purchase Details - #{purchase_id}")
        detail_window.geometry("800x600")
        
        # Create and pack the detail view
        PurchaseShowView(detail_window, purchase_id).pack(fill="both", expand=True)

    def approve_purchase(self, purchase_id, row_id):
        """Approve or reject a purchase"""
        current_status = self.tree.item(row_id, "values")[5]  # Status is at index 5
        
        if current_status == "Approved":
            Messagebox.show_info("Already Approved", "This purchase is already approved", parent=self)
            return
            
        # Ask for approval confirmation
        confirm = Messagebox.show_question(
            "Approve Purchase?",
            f"Approve purchase ID {purchase_id}?",
            parent=self,
            buttons=["Approve:success", "Reject:danger", "Cancel:secondary"]
        )
        
        if confirm == "Approve":
            new_status = "Approved"
            statusInNumber = 1
            style_tag = "Approved.TLabel"
        elif confirm == "Reject":
            new_status = "Rejected"
            statusInNumber = 2
            style_tag = "Rejected.TLabel"
        else:
            return
            
        try:
            session = Session()
            purchase = session.query(ProductPurchase).get(purchase_id)
            
            if purchase:
                purchase.status = statusInNumber
                session.commit()
                
                # Update treeview
                values = list(self.tree.item(row_id, "values"))
                values[5] = new_status
                self.tree.item(row_id, values=values, tags=(purchase_id, style_tag))
                
                Messagebox.show_info(
                    f"Purchase {new_status}",
                    f"Purchase ID {purchase_id} has been {new_status.lower()}",
                    parent=self
                )
                
            session.close()
            
        except Exception as e:
            Messagebox.show_error(f"Error updating status: {str(e)}", "Error", parent=self)

    def delete_purchase(self, purchase_id, row_id):
        """Delete a purchase"""
        confirm = Messagebox.show_question(
            "Delete Purchase?",
            f"Delete purchase ID {purchase_id}? This action cannot be undone.",
            parent=self,
            buttons=["Delete:danger", "Cancel:secondary"]
        )
        
        if confirm != "Delete":
            return
            
        try:
            session = Session()
            purchase = session.query(ProductPurchase).get(purchase_id)
            
            if purchase:
                # Delete associated purchase details first
                session.query(PurchaseDetails).filter_by(purchase_id=purchase_id).delete()
                
                # Delete the purchase
                session.delete(purchase)
                session.commit()
                
                # Remove from treeview
                self.tree.delete(row_id)
                
                # Disable buttons since selection is gone
                self.view_btn.config(state="disabled")
                self.approve_btn.config(state="disabled")
                self.delete_btn.config(state="disabled")
                
                Messagebox.show_info(
                    "Deleted",
                    f"Purchase ID {purchase_id} has been deleted",
                    parent=self
                )
                
            session.close()
            
        except Exception as e:
            Messagebox.show_error(f"Error deleting purchase: {str(e)}", "Error", parent=self)