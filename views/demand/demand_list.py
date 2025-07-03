import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from utils.database import Session
from models.demand_product import DemandProduct
from models.shop_profile import ShopProfile
from views.demand.demand_show import DemandShowView
from datetime import datetime
import re

class DemandListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.pack(fill="both", expand=True)
        
        # Pagination variables
        self.current_page = 1
        self.page_size = 10
        self.total_records = 0
        
        # Create UI
        self.create_demand_list()
        
        # Load initial data
        self.load_shops()
        self.load_demands()

    def create_demand_list(self):
        """Create the demand list interface"""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            title_frame, 
            text="DEMAND LIST", 
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
        self.shop_cb = ttk.Combobox(filter_frame, textvariable=self.shop_var, state="readonly", width=12)
        self.shop_cb.grid(row=0, column=1, padx=5, sticky="w")
        
        # Status filter
        ttk.Label(filter_frame, text="Status:", bootstyle="primary").grid(row=0, column=2, padx=2, sticky="e")
        self.status_var = ttk.StringVar(value="All")
        status_cb = ttk.Combobox(
            filter_frame, 
            textvariable=self.status_var, 
            values=["All", "Pending", "Approved", "Rejected"],
            state="readonly", 
            width=8
        )
        status_cb.grid(row=0, column=3, padx=5, sticky="w")
        
        # Date range filter
        ttk.Label(filter_frame, text="From:", bootstyle="primary").grid(row=0, column=4, padx=2, sticky="e")
        self.from_date = ttk.DateEntry(filter_frame, dateformat="%Y-%m-%d", width=9)
        self.from_date.grid(row=0, column=5, padx=5, sticky="w")
        
        ttk.Label(filter_frame, text="To:", bootstyle="primary").grid(row=0, column=6, padx=2, sticky="e")
        self.to_date = ttk.DateEntry(filter_frame, dateformat="%Y-%m-%d", width=9)
        self.to_date.grid(row=0, column=7, padx=5, sticky="w")
        
        # Filter button row (centered below the filters)
        filter_button_frame = ttk.Frame(self)
        filter_button_frame.pack(fill="x", pady=(0, 10))
        
        # Apply filter button centered
        filter_btn = ttk.Button(
            filter_button_frame, 
            text="Apply Filters", 
            command=self.load_demands,
            bootstyle="primary",
            width=15
        )
        filter_btn.pack(anchor="center", pady=5)
        
        # Treeview frame
        tree_container = ttk.Frame(self, padding=5, style="info")
        tree_container.pack(fill="both", expand=True)
        
        tree_frame = ttk.Frame(tree_container)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create Treeview
        columns = (
            "id", "shop", "date", "demand_no", "subtotal", "discount", "grand_total", 
            "status"
        )
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=8,
            bootstyle="primary",
            selectmode="browse"
        )
        
        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("shop", text="Shop")
        self.tree.heading("date", text="Date")
        self.tree.heading("demand_no", text="Demand No")
        self.tree.heading("subtotal", text="Subtotal")
        self.tree.heading("discount", text="Discount")
        self.tree.heading("grand_total", text="Grand Total")
        self.tree.heading("status", text="Status")
        
        # Set column widths
        self.tree.column("id", width=8, anchor="center")
        self.tree.column("shop", width=20, anchor="w")
        self.tree.column("date", width=15, anchor="center")
        self.tree.column("demand_no", width=10, anchor="center")
        self.tree.column("subtotal", width=10, anchor="e")
        self.tree.column("discount", width=10, anchor="e")
        self.tree.column("grand_total", width=10, anchor="e")
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
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Action buttons
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=10)
        
        self.view_btn = ttk.Button(
            action_frame, 
            text="View Details", 
            command=self.view_selected,
            bootstyle="info",
            width=15,
            state="disabled"
        )
        self.view_btn.pack(side="left", padx=10)
        
        self.approve_btn = ttk.Button(
            action_frame, 
            text="Approve", 
            command=self.approve_selected,
            bootstyle="success",
            width=15,
            state="disabled"
        )
        self.approve_btn.pack(side="left", padx=10)
        
        self.delete_btn = ttk.Button(
            action_frame, 
            text="Delete", 
            command=self.delete_selected,
            bootstyle="danger",
            width=15,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=10)
        
        refresh_btn = ttk.Button(
            action_frame, 
            text="Refresh", 
            command=self.load_demands,
            bootstyle="secondary",
            width=15
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Pagination
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(fill="x", pady=(0, 10))
        
        self.first_btn = ttk.Button(
            pagination_frame, 
            text="<< First", 
            command=lambda: self.change_page(1),
            bootstyle="primary-outline",
            width=10
        )
        self.first_btn.pack(side="left", padx=5)
        
        self.prev_btn = ttk.Button(
            pagination_frame, 
            text="< Previous", 
            command=self.prev_page,
            bootstyle="primary-outline",
            width=10
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.page_label = ttk.Label(
            pagination_frame, 
            text="Page 1 of 1", 
            bootstyle="primary",
            width=15
        )
        self.page_label.pack(side="left", padx=10)
        
        self.next_btn = ttk.Button(
            pagination_frame, 
            text="Next >", 
            command=self.next_page,
            bootstyle="primary-outline",
            width=10
        )
        self.next_btn.pack(side="left", padx=5)
        
        self.last_btn = ttk.Button(
            pagination_frame, 
            text="Last >>", 
            command=self.last_page,
            bootstyle="primary-outline",
            width=10
        )
        self.last_btn.pack(side="left", padx=5)
        
        # Bind selection event
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


    def load_demands(self):
        """Load demands from the database with filters"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        session = Session()
        try:
            # Build base query
            query = session.query(DemandProduct).join(ShopProfile)

            # --- Shop Filter ---
            selected_shop = self.shop_var.get()
            if selected_shop and selected_shop != "All Shops":
                match = re.search(r"\(ID: (\d+)\)", selected_shop)
                if match:
                    shop_id = int(match.group(1))
                    query = query.filter(DemandProduct.shop_id == shop_id)

            # --- Status Filter ---
            selected_status = self.status_var.get()
            status_map = {"Pending": 1, "Approved": 2, "Rejected": 3}
            if selected_status in status_map:
                query = query.filter(DemandProduct.approved_status == status_map[selected_status])

            # --- Date Range Filter ---
            from_date = self.from_date.entry.get()
            to_date = self.to_date.entry.get()

            if from_date:
                try:
                    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                    query = query.filter(DemandProduct.demand_date >= from_date_obj)
                except ValueError:
                    pass  # Invalid format

            if to_date:
                try:
                    to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                    query = query.filter(DemandProduct.demand_date <= to_date_obj)
                except ValueError:
                    pass

            # Get total count
            self.total_records = query.count()
            total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)

            # Apply pagination
            offset = (self.current_page - 1) * self.page_size
            demands = query.order_by(DemandProduct.created_by.desc()) \
                        .offset(offset) \
                        .limit(self.page_size) \
                        .all()

            print(f"Loaded {len(demands)} demands")

            # Populate treeview
            for demand in demands:
                shop = demand.shop
                shop_name = f"{shop.shop_name} (ID: {shop.id})" if shop else "N/A"

                status_str = {1: "Pending", 2: "Approved", 3: "Rejected"}.get(demand.approved_status, "Pending")
                status_style = "success" if status_str == "Approved" else "warning" if status_str == "Pending" else "danger"

                self.tree.insert(
                    "", 
                    "end", 
                    values=(
                        demand.id,
                        shop_name,
                        demand.demand_date.strftime("%Y-%m-%d"),
                        demand.demand_no or "N/A",
                        f"₹{demand.sub_total:.2f}",
                        f"₹{demand.discount:.2f}",
                        f"₹{demand.grand_total:.2f}",
                        status_str
                    ),
                    tags=(demand.id, status_style)
                )

            self.update_pagination_controls(total_pages)

        except Exception as e:
            Messagebox.show_error(f"Error loading demands: {str(e)}", "Error", parent=self)
        finally:
            session.close()

    def update_pagination_controls(self, total_pages):
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")
        self.first_btn.config(state="normal" if self.current_page > 1 else "disabled")
        self.prev_btn.config(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < total_pages else "disabled")
        self.last_btn.config(state="normal" if self.current_page < total_pages else "disabled")
    
    def change_page(self, page):
        if page != self.current_page:
            self.current_page = page
            self.load_demands()
    
    def prev_page(self):
        if self.current_page > 1:
            self.change_page(self.current_page - 1)
    
    def next_page(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.change_page(self.current_page + 1)
    
    def last_page(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.change_page(total_pages)
    
    def on_selection_change(self, event):
        selected = self.tree.selection()
        if selected:
            self.view_btn.config(state="normal")
            status = self.tree.item(selected[0], "values")[7]
            self.approve_btn.config(state="normal" if status != "Approved" else "disabled")
            self.delete_btn.config(state="normal")
        else:
            self.view_btn.config(state="disabled")
            self.approve_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
    
    def get_selected_demand_id(self):
        selected = self.tree.selection()
        if selected:
            tags = self.tree.item(selected[0], "tags")
            if tags:
                return tags[0]
        return None
    
    def on_double_click(self, event):
        demand_id = self.get_selected_demand_id()
        if demand_id:
            self.view_demand_details(demand_id)
    
    def view_selected(self):
        demand_id = self.get_selected_demand_id()
        if demand_id:
            self.view_demand_details(demand_id)
    
    def view_demand_details(self, demand_id):
        detail_window = ttk.Toplevel(self)
        detail_window.title(f"Demand Details - #{demand_id}")
        detail_window.geometry("800x600")
        DemandShowView(detail_window, demand_id).pack(fill="both", expand=True)
    
    def approve_selected(self):
        demand_id = self.get_selected_demand_id()
        if demand_id:
            selected = self.tree.selection()
            self.approve_demand(demand_id, selected[0])
    
    def approve_demand(self, demand_id, row_id):
        current_status = self.tree.item(row_id, "values")[7]
        
        if current_status == "Approved":
            Messagebox.show_info("Already Approved", "This demand is already approved", parent=self)
            return
            
        confirm = Messagebox.show_question(
            "Approve Demand?",
            f"Approve demand ID {demand_id}?",
            parent=self,
            buttons=["Approve:success", "Reject:danger", "Cancel:secondary"]
        )
        
        if confirm == "Approve":
            new_status = 2  # Approved
            status_str = "Approved"
            style_tag = "success"
        elif confirm == "Reject":
            new_status = 3  # Rejected
            status_str = "Rejected"
            style_tag = "danger"
        else:
            return
            
        try:
            session = Session()
            demand = session.query(DemandProduct).get(demand_id)
            
            if demand:
                demand.approved_status = new_status
                demand.approved_at = datetime.now()
                session.commit()
                
                values = list(self.tree.item(row_id, "values"))
                values[7] = status_str
                self.tree.item(row_id, values=values, tags=(demand_id, style_tag))
                
                if new_status == 2:
                    self.approve_btn.config(state="disabled")
                
                Messagebox.show_info(
                    f"Demand {status_str}",
                    f"Demand ID {demand_id} has been {status_str.lower()}",
                    parent=self
                )
                
            session.close()
            
        except Exception as e:
            Messagebox.show_error(f"Error updating status: {str(e)}", "Error", parent=self)

    def delete_selected(self):
        demand_id = self.get_selected_demand_id()
        if demand_id:
            selected = self.tree.selection()
            self.delete_demand(demand_id, selected[0])
    
    def delete_demand(self, demand_id, row_id):
        confirm = Messagebox.show_question(
            "Delete Demand?",
            f"Delete demand ID {demand_id}? This action cannot be undone.",
            parent=self,
            buttons=["Delete:danger", "Cancel:secondary"]
        )
        
        if confirm != "Delete":
            return
            
        try:
            session = Session()
            demand = session.query(DemandProduct).get(demand_id)
            
            if demand:
                # Delete associated details first
                session.query(DemandDetails).filter_by(demand_id=demand_id).delete()
                
                # Delete the demand
                session.delete(demand)
                session.commit()
                
                # Remove from treeview
                self.tree.delete(row_id)
                
                # Disable buttons
                self.view_btn.config(state="disabled")
                self.approve_btn.config(state="disabled")
                self.delete_btn.config(state="disabled")
                
                # Reload data
                self.load_demands()
                
                Messagebox.show_info(
                    "Deleted",
                    f"Demand ID {demand_id} has been deleted",
                    parent=self
                )
                
            session.close()
            
        except Exception as e:
            Messagebox.show_error(f"Error deleting demand: {str(e)}", "Error", parent=self)