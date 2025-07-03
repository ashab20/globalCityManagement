import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from utils.database import Session
from models.shop_profile import ShopProfile
from models.product import Product
from models.product_purchase import ProductPurchase
from models.purchase_details import PurchaseDetails
from datetime import datetime
import os
import tempfile
import webbrowser
from PIL import Image, ImageTk

class PurchaseShowView(ttk.Frame):
    def __init__(self, parent, purchase_id):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.purchase_id = purchase_id
        self.pack(fill="both", expand=True)
        
        # Load data
        self.load_purchase_details()
        
        # Create invoice view
        self.create_invoice_view()
    
    def load_purchase_details(self):
        """Load purchase details from database"""
        try:
            session = Session()
            self.purchase = session.query(ProductPurchase).get(self.purchase_id)
            self.shop = session.query(ShopProfile).get(self.purchase.shop_id)
            self.details = session.query(PurchaseDetails).filter_by(purchase_id=self.purchase_id).all()
            
            # Get product names
            self.product_names = {}
            for detail in self.details:
                product = session.query(Product).get(detail.product_id)
                if product:
                    self.product_names[detail.product_id] = product.name
                    
            session.close()
        except Exception as e:
            Messagebox.show_error(f"Error loading details: {str(e)}", "Error", parent=self)

    def create_invoice_view(self):
        """Create the invoice-like display"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Left: Logo and shop info
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side="left", fill="y")
        
        # Try to load logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'assets', 'images', 'logo.png')
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).resize((150, 50), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(logo_img)
                ttk.Label(left_frame, image=self.logo).pack(pady=(0, 10))
            except Exception as e:
                print(f"Error loading logo: {str(e)}")
        
        ttk.Label(left_frame, text=self.shop.shop_name, font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(left_frame, text=self.shop.shop_no or "Address not provided").pack(anchor="w")
        ttk.Label(left_frame, text=f"Floot: {self.shop.floor_no or 'N/A'}").pack(anchor="w")
        ttk.Label(left_frame, text=f"Description: {self.shop.descreption or 'N/A'}").pack(anchor="w")
        
        # Right: Invoice info
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side="right", fill="y")
        
        ttk.Label(
            right_frame, 
            text="PURCHASE INVOICE", 
            font=("Helvetica", 18, "bold"), 
            bootstyle="primary"
        ).pack(anchor="e")
        
        ttk.Label(right_frame, text=f"Invoice #: {self.purchase.id}", font=("Helvetica", 10, "bold")).pack(anchor="e")
        ttk.Label(right_frame, text=f"Date: {self.purchase.purchase_date.strftime('%B %d, %Y')}").pack(anchor="e")
        
        # Status indicator with color
        status_style = "success" if self.purchase.status == 1 else "warning" if self.purchase.status == 2 else "danger"
        ttk.Label(
            right_frame, 
            text=f"Status: {self.purchase.status == 1 and 'Approved' or self.purchase.status == 2 and  'Rejected' or 'Pending'}", 
            bootstyle=f"{status_style}, inverse",
            font=("Helvetica", 10, "bold")
        ).pack(anchor="e", pady=(5, 0))
        
        # Separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Products section
        products_frame = ttk.LabelFrame(main_frame, text="Products", padding=10)
        products_frame.pack(fill="x", pady=(0, 20))
        
        # Table header
        header_row = ttk.Frame(products_frame)
        header_row.pack(fill="x", pady=(0, 5))
        
        headers = ["Product", "Quantity", "Unit Price", "Total"]
        widths = [40, 15, 15, 15]
        
        for header, width in zip(headers, widths):
            lbl = ttk.Label(
                header_row, 
                text=header, 
                width=width, 
                anchor="w", 
                font=("Helvetica", 10, "bold")
            )
            lbl.configure(background="#4361ee", foreground="white")
            lbl.pack(side="left", padx=5)
        
        # Products list
        for i, detail in enumerate(self.details):
            row_frame = ttk.Frame(products_frame)
            row_frame.pack(fill="x", pady=2)
            
            # Apply alternating background
            if i % 2 == 0:
                row_frame.configure(style="TFrame")  # Default style
            else:
                row_frame.configure(style="Secondary.TFrame")  # Light gray background
            
            # Product name
            product_name = self.product_names.get(detail.product_id, f"Product #{detail.product_id}")
            ttk.Label(row_frame, text=product_name, width=40, anchor="w").pack(side="left", padx=5)
            
            # Quantity
            ttk.Label(row_frame, text=str(detail.quantity), width=15, anchor="w").pack(side="left", padx=5)
            
            # Unit price
            ttk.Label(row_frame, text=f"₹{detail.unit_price:.2f}", width=15, anchor="w").pack(side="left", padx=5)
            
            # Total
            ttk.Label(row_frame, text=f"₹{detail.total:.2f}", width=15, anchor="w").pack(side="left", padx=5)
        
        # Totals section
        totals_frame = ttk.Frame(main_frame)
        totals_frame.pack(fill="x", anchor="e", pady=(0, 20))
        
        # Subtotal
        ttk.Label(totals_frame, text="Subtotal:", width=15, anchor="e").grid(row=0, column=0, sticky="e", padx=5)
        ttk.Label(totals_frame, text=f"₹{self.purchase.sub_total:.2f}", width=15, anchor="w").grid(row=0, column=1, padx=5)
        
        # Discount
        ttk.Label(totals_frame, text="Discount:", width=15, anchor="e").grid(row=1, column=0, sticky="e", padx=5)
        ttk.Label(totals_frame, text=f"-₹{self.purchase.discount:.2f}", width=15, anchor="w").grid(row=1, column=1, padx=5)
        
        # Grand Total
        ttk.Label(totals_frame, text="Grand Total:", width=15, anchor="e", font=("Helvetica", 10, "bold")).grid(
            row=2, column=0, sticky="e", padx=5, pady=(10, 0))
        ttk.Label(totals_frame, text=f"₹{self.purchase.grand_total:.2f}", width=15, anchor="w", 
                font=("Helvetica", 10, "bold")).grid(row=2, column=1, padx=5, pady=(10, 0))
        
        # Notes section
        notes_frame = ttk.LabelFrame(main_frame, text="Notes & Comments", padding=10)
        notes_frame.pack(fill="x")
        
        ttk.Label(
            notes_frame, 
            text="Thank you for your business!",
            wraplength=600
        ).pack(anchor="w", fill="x")
        
        # Footer section
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=20)
        
        # Signature
        ttk.Label(footer_frame, text="Authorized Signature: ___________________", anchor="w").pack(side="left")
        
        # Print button
        print_btn = ttk.Button(
            footer_frame, 
            text="Print Invoice", 
            command=self.print_invoice,
            bootstyle="primary",
            width=15
        )
        print_btn.pack(side="right", padx=10)
        
        # Close button
        close_btn = ttk.Button(
            footer_frame, 
            text="Close", 
            command=self.parent.destroy,
            bootstyle="secondary",
            width=15
        )
        close_btn.pack(side="right", padx=10)
    
    def print_invoice(self):
        """Generate and print the invoice as HTML"""
        try:
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Purchase Invoice #{self.purchase.id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .invoice-container {{ width: 800px; margin: 0 auto; padding: 20px; }}
                    .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                    .invoice-title {{ text-align: right; }}
                    .section {{ background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; }}
                    .table {{ width: 100%; border-collapse: collapse; }}
                    .table th {{ background-color: #4361ee; color: white; text-align: left; padding: 8px; }}
                    .table tr:nth-child(even) {{ background-color: #f8f9fa; }}
                    .table td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                    .totals {{ text-align: right; margin-bottom: 20px; }}
                    .footer {{ margin-top: 30px; display: flex; justify-content: space-between; }}
                    .signature {{ margin-top: 50px; }}
                    .total-row {{ font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="invoice-container">
                    <div class="header">
                        <div class="shop-info">
                            <h2>{self.shop.shop_name}</h2>
                            <p>{self.shop.floor_no or 'Address not provided'}</p>
                            <p>Description: {self.shop.descreption or 'N/A'}</p>
                        </div>
                        <div class="invoice-title">
                            <h1>PURCHASE INVOICE</h1>
                            <p><strong>Invoice #:</strong> {self.purchase.id}</p>
                            <p><strong>Date:</strong> {self.purchase.purchase_date.strftime('%B %d, %Y')}</p>
                            <p><strong>Status:</strong> <span style="background-color: {'#28a745' if self.purchase.status == 'Approved' else '#ffc107' if self.purchase.status == 'Pending' else '#dc3545'}; color: white; padding: 2px 5px; border-radius: 3px;">{self.purchase.status}</span></p>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <div class="section">
                        <h3>Products</h3>
                        <table class="table">
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                            </tr>
            """
            
            # Add products
            for detail in self.details:
                product_name = self.product_names.get(detail.product_id, f"Product #{detail.product_id}")
                html_content += f"""
                <tr>
                    <td>{product_name}</td>
                    <td>{detail.quantity}</td>
                    <td>₹{detail.unit_price:.2f}</td>
                    <td>₹{detail.total:.2f}</td>
                </tr>
                """
            
            html_content += f"""
                        </table>
                    </div>
                    
                    <div class="totals">
                        <p><strong>Subtotal:</strong> ₹{self.purchase.sub_total:.2f}</p>
                        <p><strong>Discount:</strong> ₹{self.purchase.discount:.2f}</p>
                        <p class="total-row"><strong>Grand Total:</strong> ₹{self.purchase.grand_total:.2f}</p>
                    </div>
                    
                    <div class="section">
                        <h3>Notes & Comments</h3>
                        <p>Thank you for your business!</p>
                    </div>
                    
                    <div class="footer">
                        <div class="signature">
                            <p>Authorized Signature: ___________________</p>
                        </div>
                        <div class="print-info">
                            <p>Printed on: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
                f.write(html_content)
                temp_file = f.name
            
            # Open in browser for printing
            webbrowser.open(f"file://{temp_file}")
            
            Messagebox.show_info(
                "Invoice Ready",
                "The invoice has been generated. Please use the browser's print function to print it.",
                parent=self
            )
            
        except Exception as e:
            Messagebox.show_error(
                f"Failed to generate invoice: {str(e)}",
                "Error",
                parent=self
            )