from tkinter import StringVar, IntVar
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from utils.database import Session
from models.product_purchase import ProductPurchase
from models.purchase_details import PurchaseDetails
from models.product import Product
from models.shop_profile import ShopProfile

class Purchase(ttk.Frame):
    def __init__(self, parent, existing_purchase=None):
        super().__init__(parent)
        self.parent = parent
        self.existing_purchase = existing_purchase  
        self.shop_id = StringVar()
        self.purchase_date = StringVar()
        self.discount = IntVar(value=0)
        self.subtotal = IntVar(value=0)
        self.grand_total = IntVar(value=0)

        self.rows = []
        self.row_colors = ["#f5f5f5", "#ffffff"]  # Alternate row colors

        # Create custom styles
        self.create_styles()
        
        self.load_product_list()
        self.load_shop_list()
        self.create_form()
        self.pack(fill="both", expand=True)

    def create_styles(self):
        """Create custom styles for the purchase view"""
        style = ttk.Style()
        
        # Repeater section background
        style.configure("Repeater.TFrame", background="#f8f9fa", borderwidth=1, relief="solid")
        
        # Header styles
        style.configure("Header.TLabel", 
                        background="#4361ee", 
                        foreground="white", 
                        font=("Helvetica", 10, "bold"),
                        padding=5)
        
        # Row styles
        style.configure("Row1.TFrame", background="#f5f5f5")
        style.configure("Row2.TFrame", background="#ffffff")
        
        # Button styles
        style.configure("Delete.TButton", font=("Helvetica", 9), padding=0)

    def create_form(self):
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(fill="x", pady=4, padx=5)

        # Title with increased width
        title_frame = ttk.Frame(self.form_frame, style="primary")
        title_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(
            title_frame, 
            text="PURCHASE ENTRY", 
            font=("Helvetica", 16, "bold"), 
            bootstyle="inverse-primary",
            width=20  # Increased width
        ).pack(pady=5, anchor="center")

        # Shop and date inputs
        input_row = ttk.Frame(self.form_frame)
        input_row.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(input_row, text="Shop:", bootstyle="primary", width=10, anchor="e").grid(row=0, column=0, sticky="e")
        self.shop_combobox = ttk.Combobox(input_row, state="readonly", textvariable=self.shop_id, width=15)
        self.shop_combobox.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_row, text="Purchase Date:", bootstyle="primary", width=10, anchor="e").grid(row=0, column=2, sticky="e")
        self.purchase_date_picker = ttk.DateEntry(input_row, dateformat="%Y-%m-%d", width=15, bootstyle="primary")
        self.purchase_date_picker.grid(row=0, column=3, padx=5, pady=5)

        # Repeater section with distinct background
        repeater_frame = ttk.Frame(self.form_frame, style="Repeater.TFrame")
        repeater_frame.pack(fill="x", padx=10, pady=10)

        # Table Headers with increased width and custom style
        headers = ttk.Frame(repeater_frame)
        headers.pack(fill="x", padx=5, pady=(5, 0))
        
        # Increased widths for headers
        header_widths = [32, 15, 15, 8, 8]
        for text, w in zip(["Product", "Qty", "Price", "Subtotal", "Action"], header_widths):
            header = ttk.Label(
                headers, 
                text=text, 
                width=w, 
                anchor="w", 
                style="Header.TLabel"
            )
            header.pack(side="left", padx=5, pady=2)

        # Product Rows container
        self.rows_container = ttk.Frame(repeater_frame)
        self.rows_container.pack(fill="x", padx=5, pady=(0, 5))
        self.add_row()

        # Add Row Button
        ttk.Button(
            repeater_frame, 
            text="+ Add Row", 
            command=self.add_row, 
            bootstyle="success-outline",
            width=15
        ).pack(anchor="e", padx=5, pady=5)

        # Total & Discount Summary
        summary_frame = ttk.Frame(self.form_frame)
        summary_frame.pack(fill="x", padx=20, pady=10)

        # Create summary labels with increased width
        summary_width = 15
        ttk.Label(summary_frame, text="Subtotal:", width=summary_width, anchor="e").pack(side="left", padx=5)
        ttk.Label(summary_frame, textvariable=self.subtotal, width=15, anchor="w").pack(side="left", padx=5)

        ttk.Label(summary_frame, text="Discount:", width=summary_width, anchor="e").pack(side="left", padx=5)
        self.discount_entry = ttk.Entry(summary_frame, textvariable=self.discount, width=15)
        self.discount_entry.pack(side="left", padx=5)
        self.discount.trace_add("write", lambda *args: self.update_summary())

        ttk.Label(summary_frame, text="Grand Total:", width=summary_width, anchor="e").pack(side="left", padx=5)
        total_label = ttk.Label(summary_frame, textvariable=self.grand_total, width=15, anchor="w", 
                              font=("Helvetica", 10, "bold"), bootstyle="success")
        total_label.pack(side="left", padx=5)

        # Submit button with increased width
        ttk.Button(
            self.form_frame, 
            text="SUBMIT PURCHASE", 
            command=self.submit_purchase, 
            bootstyle="primary",
            width=20
        ).pack(anchor="center", pady=10)

        self.set_shop_combobox_values()

    def add_row(self):
        row_frame = ttk.Frame(self.rows_container)
        row_frame.pack(fill="x", pady=2)
        
        # Set alternating background color
        row_style = f"Row{len(self.rows) % 2 + 1}.TFrame"
        row_frame.configure(style=row_style)

        product_var = StringVar()
        qty_var = IntVar(value=1)
        price_var = IntVar(value=0)
        total_var = IntVar(value=0)

        # Create widgets with increased widths to match headers
        product_cb = ttk.Combobox(
            row_frame, 
            textvariable=product_var, 
            values=list(self.product_mapping.keys()), 
            width=20
        )
        product_cb.pack(side="left", padx=5)

        qty_entry = ttk.Entry(row_frame, textvariable=qty_var, width=10)
        qty_entry.pack(side="left", padx=5)

        price_entry = ttk.Entry(row_frame, textvariable=price_var, width=10)
        price_entry.pack(side="left", padx=5)

        total_label = ttk.Label(row_frame, textvariable=total_var, width=10, anchor="w")
        total_label.pack(side="left", padx=5)

        # Delete button with custom style
        delete_btn = ttk.Button(
            row_frame, 
            text="Delete", 
            width=10,
            bootstyle="danger",
            command=lambda f=row_frame: self.delete_row(f)
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
            "total_var": total_var,
        })

        self.update_summary()
        
    def delete_row(self, row_frame):
        """Delete a row from the form."""
        # Find the row in our list
        row_to_delete = None
        for row in self.rows:
            if row["frame"] == row_frame:
                row_to_delete = row
                break
                
        if row_to_delete:
            # Remove from UI and list
            row_frame.destroy()
            self.rows.remove(row_to_delete)
            
            # Update row colors
            for i, row in enumerate(self.rows):
                row_style = f"Row{i % 2 + 1}.TFrame"
                row["frame"].configure(style=row_style)
            
            self.update_summary()

    def update_summary(self):
        subtotal = 0
        for row in self.rows:
            try:
                qty = row["qty_var"].get()
                price = row["price_var"].get()
                subtotal += qty * price
            except:
                pass  # Ignore invalid values
                
        self.subtotal.set(subtotal)
        discount = self.discount.get()
        self.grand_total.set(max(0, subtotal - discount))

    def load_product_list(self):
        session = Session()
        products = session.query(Product).all()
        session.close()
        self.product_mapping = {f"{p.name} (ID: {p.id})": p.id for p in products}

    def load_shop_list(self):
        session = Session()
        shops = session.query(ShopProfile).all()
        session.close()
        self.shop_mapping = {f"{s.shop_name} (ID: {s.id})": s.id for s in shops}

    def set_shop_combobox_values(self):
        self.shop_combobox['values'] = list(self.shop_mapping.keys())

    def submit_purchase(self):
        try:
            shop_name = self.shop_combobox.get()
            shop_id = self.shop_mapping.get(shop_name)
            purchase_date = self.purchase_date_picker.entry.get()
            discount = self.discount.get()
            subtotal = self.subtotal.get()
            grand_total = self.grand_total.get()

            if not shop_id or not purchase_date:
                raise Exception("Shop and Date are required.")
                
            if not self.rows:
                raise Exception("No products added to the purchase.")
                
            # Validate all rows have valid products
            for i, row in enumerate(self.rows):
                if not self.product_mapping.get(row["product_var"].get()):
                    raise Exception(f"Row {i+1} has an invalid product selection")

            session = Session()
            new_purchase = ProductPurchase(
                shop_id=shop_id,
                purchase_date=datetime.strptime(purchase_date, "%Y-%m-%d"),
                sub_total=subtotal,
                discount=discount,
                grand_total=grand_total,
                status=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(new_purchase)
            session.flush()

            for row in self.rows:
                product_id = self.product_mapping.get(row["product_var"].get())
                qty = row["qty_var"].get()
                price = row["price_var"].get()
                total = qty * price

                if not product_id or qty <= 0 or price <= 0:
                    continue

                detail = PurchaseDetails(
                    purchase_id=new_purchase.id,
                    product_id=product_id,
                    quantity=qty,
                    unit_price=price,
                    total=total
                )
                session.add(detail)

            session.commit()
            Messagebox.show_info("Success", "Purchase saved successfully!", parent=self)

            # Clear form after successful submission
            self.clear_form()

        except Exception as e:
            Messagebox.show_error("Error", f"Failed to save: {str(e)}", parent=self)
            
    def clear_form(self):
        """Clear the form after successful submission"""
        # Clear rows
        for row in self.rows:
            row["frame"].destroy()
        self.rows = []
        
        # Add one empty row
        self.add_row()
        
        # Reset values
        self.shop_id.set("")
        self.purchase_date_picker.entry.delete(0, "end")
        self.discount.set(0)
        self.subtotal.set(0)
        self.grand_total.set(0)