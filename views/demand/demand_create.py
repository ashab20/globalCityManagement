import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from utils.database import Session
from models.demand_product import DemandProduct
from models.demand_details import DemandDetails
from models.shop_profile import ShopProfile
from models.product import Product
from datetime import datetime

class DemandCreateView(ttk.Frame):
    def __init__(self, parent, existing_demand=None):
        super().__init__(parent, padding=5)
        self.parent = parent
        self.existing_demand = existing_demand
        self.shop_id = ttk.StringVar()
        self.demand_date = ttk.StringVar()
        self.demand_no = ttk.StringVar()
        self.discount = ttk.IntVar(value=0)
        self.subtotal = ttk.IntVar(value=0)
        self.grand_total = ttk.IntVar(value=0)

        self.rows = []
        self.row_colors = ["#f5f5f5", "#ffffff"]
        self.style = ttk.Style()
        self.style.configure("RowColor1.TFrame", background="#f5f5f5")
        self.style.configure("RowColor2.TFrame", background="#ffffff")

        self.load_product_list()
        self.load_shop_list()
        self.create_form()
        self.pack(fill="both", expand=True)

    def create_form(self):
        """Create the demand creation form"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            title_frame, 
            text="CREATE DEMAND", 
            font=("Helvetica", 16, "bold"), 
            bootstyle="inverse-primary",
            anchor="center"
        ).pack(fill="x", pady=5)
        
        # Shop and date inputs
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(input_frame, text="Shop:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5)
        self.shop_cb = ttk.Combobox(input_frame, textvariable=self.shop_id, state="readonly", width=10)
        self.shop_cb.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Demand Date:", width=15, anchor="e").grid(row=0, column=2, padx=5, pady=5)
        self.date_entry = ttk.DateEntry(input_frame, dateformat="%Y-%m-%d", width=10)
        self.date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Demand No:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5)
        self.demand_no_entry = ttk.Entry(input_frame, textvariable=self.demand_no, width=10)
        self.demand_no_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Products section
        products_frame = ttk.LabelFrame(main_frame, text="Products", padding=10)
        products_frame.pack(fill="x", pady=(0, 5))
        
        # Table headers
        header_frame = ttk.Frame(products_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        headers = ["Product", "Quantity", "Unit Price", "Total", "Action"]
        widths = [34, 12, 15, 15, 10]
        
        for header, width in zip(headers, widths):
            lbl = ttk.Label(
                header_frame, 
                text=header, 
                width=width, 
                anchor="w", 
                font=("Helvetica", 10, "bold")
            )
            lbl.configure(background="#4361ee", foreground="white")
            lbl.pack(side="left", padx=5)
        
        # Products container
        self.products_container = ttk.Frame(products_frame)
        self.products_container.pack(fill="x", pady=(0, 10))
        self.add_row()
        
        # Add row button
        add_btn = ttk.Button(
            products_frame, 
            text="+ Add Product", 
            command=self.add_row,
            bootstyle="success",
            width=10
        )
        add_btn.pack(anchor="e", padx=5, pady=5)
        
        # Totals section
        totals_frame = ttk.Frame(main_frame)
        totals_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(totals_frame, text="Subtotal:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(totals_frame, textvariable=self.subtotal, width=20, anchor="w").grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(totals_frame, text="Discount:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=2)
        discount_entry = ttk.Entry(totals_frame, textvariable=self.discount, width=20)
        discount_entry.grid(row=1, column=1, padx=5, pady=2)
        self.discount.trace_add("write", lambda *args: self.update_summary())
        
        ttk.Label(totals_frame, text="Grand Total:", width=15, anchor="e", font=("Helvetica", 10, "bold")).grid(
            row=2, column=0, padx=5, pady=2)
        ttk.Label(totals_frame, textvariable=self.grand_total, width=20, anchor="w", 
                font=("Helvetica", 10, "bold")).grid(row=2, column=1, padx=5, pady=2)
        
        # Submit button
        submit_btn = ttk.Button(
            main_frame, 
            text="Submit Demand", 
            command=self.submit_demand,
            bootstyle="primary",
            width=20
        )
        submit_btn.pack(anchor="center", pady=20)
        
        # Set shop values
        self.set_shop_combobox_values()

    def add_row(self):
        """Add a new product row to the form"""
        color_index = len(self.rows) % 2
        style_name = f"RowColor{color_index+1}.TFrame"
        row_frame = ttk.Frame(self.products_container, style=style_name)
        row_frame.pack(fill="x", pady=2)
        
        product_var = ttk.StringVar()
        qty_var = ttk.IntVar(value=1)
        price_var = ttk.IntVar(value=0)
        total_var = ttk.IntVar(value=0)
        
        # Product combobox
        product_cb = ttk.Combobox(
            row_frame, 
            textvariable=product_var, 
            values=list(self.product_mapping.keys()), 
            width=20
        )
        product_cb.pack(side="left", padx=5)
        
        # Quantity entry
        qty_entry = ttk.Entry(row_frame, textvariable=qty_var, width=7)
        qty_entry.pack(side="left", padx=5)
        
        # Price entry
        price_entry = ttk.Entry(row_frame, textvariable=price_var, width=10)
        price_entry.pack(side="left", padx=15)
        
        # Total label
        total_label = ttk.Label(row_frame, textvariable=total_var, width=10, anchor="w")
        total_label.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ttk.Button(
            row_frame, 
            text="Delete", 
            command=lambda f=row_frame: self.delete_row(f),
            bootstyle="danger",
            width=10
        )
        delete_btn.pack(side="left", padx=5)
        
        def update_total(*args):
            try:
                total = qty_var.get() * price_var.get()
                total_var.set(total)
                self.update_summary()
            except:
                total_var.set(0)
        
        qty_var.trace_add("write", update_total)
        price_var.trace_add("write", update_total)
        
        self.rows.append({
            "frame": row_frame,
            "product_var": product_var,
            "qty_var": qty_var,
            "price_var": price_var,
            "total_var": total_var
        })
        
        self.update_summary()
    
    def delete_row(self, row_frame):
        """Delete a product row from the form"""
        row_to_delete = None
        for row in self.rows:
            if row["frame"] == row_frame:
                row_to_delete = row
                break
                
        if row_to_delete:
            row_frame.destroy()
            self.rows.remove(row_to_delete)
            
            # Update styles after deletion
            for i, row in enumerate(self.rows):
                color_index = i % 2
                style_name = f"RowColor{color_index+1}.TFrame"
                row["frame"].configure(style=style_name)
            
            self.update_summary()
    
    def update_summary(self):
        """Update subtotal and grand total"""
        subtotal = 0
        for row in self.rows:
            try:
                subtotal += row["qty_var"].get() * row["price_var"].get()
            except:
                pass
                
        self.subtotal.set(subtotal)
        discount = self.discount.get()
        self.grand_total.set(max(0, subtotal - discount))
    
    def load_product_list(self):
        """Load products for combobox"""
        try:
            session = Session()
            products = session.query(Product).all()
            session.close()
            self.product_mapping = {f"{p.name} (ID: {p.id})": p.id for p in products}
        except Exception as e:
            Messagebox.show_error(f"Error loading products: {str(e)}", "Error", parent=self)
    
    def load_shop_list(self):
        """Load shops for combobox"""
        try:
            session = Session()
            shops = session.query(ShopProfile).all()
            session.close()
            self.shop_mapping = {f"{s.shop_name} (ID: {s.id})": s.id for s in shops}
        except Exception as e:
            Messagebox.show_error(f"Error loading shops: {str(e)}", "Error", parent=self)
    
    def set_shop_combobox_values(self):
        """Set values in shop combobox"""
        self.shop_cb['values'] = list(self.shop_mapping.keys())
    
    def submit_demand(self):
        """Submit the demand to the database"""
        try:
            shop_name = self.shop_cb.get()
            shop_id = self.shop_mapping.get(shop_name)
            demand_date = self.date_entry.entry.get()
            demand_no = self.demand_no.get()
            discount = self.discount.get()
            subtotal = self.subtotal.get()
            grand_total = self.grand_total.get()
            
            if not shop_id or not demand_date:
                raise Exception("Shop and Date are required")
                
            if not self.rows:
                raise Exception("At least one product is required")
                
            # Validate products
            for i, row in enumerate(self.rows):
                if not self.product_mapping.get(row["product_var"].get()):
                    raise Exception(f"Row {i+1} has an invalid product")
            
            session = Session()
            new_demand = DemandProduct(
                shop_id=shop_id,
                demand_date=datetime.strptime(demand_date, "%Y-%m-%d"),
                demand_no=demand_no,
                sub_total=subtotal,
                discount=discount,
                grand_total=grand_total,
                status=1,
                approved_status=1,  # Pending
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(new_demand)
            session.flush()  # Get the new ID
            
            # Add demand details
            for row in self.rows:
                product_id = self.product_mapping.get(row["product_var"].get())
                qty = row["qty_var"].get()
                price = row["price_var"].get()
                total = qty * price
                
                if product_id and qty > 0 and price > 0:
                    detail = DemandDetails(
                        demand_id=new_demand.id,
                        product_id=product_id,
                        quantity=qty,
                        unit_price=price,
                        total=total
                    )
                    session.add(detail)
            
            session.commit()
            Messagebox.show_info("Success", "Demand created successfully!", parent=self)
            
            # Clear form
            self.clear_form()
            
        except Exception as e:
            Messagebox.show_error(f"Error creating demand: {str(e)}", "Error", parent=self)
    
    def clear_form(self):
        """Clear the form after submission"""
        # Clear rows
        for row in self.rows:
            row["frame"].destroy()
        self.rows = []
        
        # Add one row
        self.add_row()
        
        # Reset values
        self.shop_id.set("")
        self.date_entry.entry.delete(0, "end")
        self.demand_no.set("")
        self.discount.set(0)
        self.subtotal.set(0)
        self.grand_total.set(0)