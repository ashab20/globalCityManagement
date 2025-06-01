     
    
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.bill_info import BillInfo
from models.bill_particular import BillParticular
from models.shop_profile import ShopProfile
from utils.database import Session
from tkinter.messagebox import showinfo, showerror

# PDF GENERATION
import os
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from fpdf import FPDF
# import os
# import subprocess
# from tkinter.messagebox import showinfo, showerror

class BillDetailView(ttk.Frame):
    def __init__(self, parent, bill_id):
        super().__init__(parent, padding=20)
        self.bill_id = bill_id
        self.parent = parent
        self.style = ttk.Style()
        
        self.configure_styles()
        self.create_widgets()
        self.load_bill_data()

    def configure_styles(self):
        self.style.configure("TFrame", background="white")
        self.style.configure("TLabel", background="white", font=("Helvetica", 10))
        self.style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # Header Section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=10)
        
        self.title_label = ttk.Label(
            header_frame, 
            text="Bill Details",
            style="Title.TLabel",
            bootstyle=PRIMARY
        )
        self.title_label.pack(side="left")
        
        # Print Button
        ttk.Button(
            header_frame,
            text="Print Bill",
            command=self.print_bill,
            bootstyle=INFO,
            width=15
        ).pack(side="right", padx=10)

        # Bill Information Section
        info_frame = ttk.LabelFrame(main_frame, text="Bill Information", padding=10)
        info_frame.pack(fill="x", pady=10)

        self.create_info_rows(info_frame)
        
        # Particulars Section
        particulars_frame = ttk.LabelFrame(main_frame, text="Bill Particulars", padding=10)
        particulars_frame.pack(fill="both", expand=True, pady=10)

        # Treeview for particulars
        columns = ("Particular", "Quantity", "Unit", "Rate", "Amount")
        self.particulars_tree = ttk.Treeview(
            particulars_frame,
            columns=columns,
            show="headings",
            bootstyle=PRIMARY,
            height=6
        )

        for col in columns:
            self.particulars_tree.heading(col, text=col)
            self.particulars_tree.column(col, width=120, anchor=CENTER)

        scrollbar = ttk.Scrollbar(particulars_frame, orient=VERTICAL, command=self.particulars_tree.yview)
        self.particulars_tree.configure(yscrollcommand=scrollbar.set)

        self.particulars_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def create_info_rows(self, parent):
        rows = [
            ("Shop:", "shop_info"),
            ("Bill Date:", "bill_date"),
            ("Period:", "bill_period"),
            ("Month:", "bill_month"),
            ("Year:", "bill_year"),
            ("Total Amount:", "total_amount"),
            ("Previous Due:", "prev_due"),
            ("Status:", "status")
        ]

        # Iterate in steps of 2 to process two items per row
        for i in range(0, len(rows), 2):
            frame = ttk.Frame(parent)
            frame.pack(fill="x", pady=2)

            # First label-value pair
            label_text1, var_name1 = rows[i]
            ttk.Label(frame, text=label_text1, width=15, style="Header.TLabel").pack(side=LEFT)
            setattr(self, var_name1, ttk.Label(frame, text="", width=20))
            getattr(self, var_name1).pack(side=LEFT, padx=(0, 20))

            # Second label-value pair, if it exists
            if i + 1 < len(rows):
                label_text2, var_name2 = rows[i + 1]
                ttk.Label(frame, text=label_text2, width=15, style="Header.TLabel").pack(side=LEFT)
                setattr(self, var_name2, ttk.Label(frame, text="", width=20))
                getattr(self, var_name2).pack(side=LEFT)


    def load_bill_data(self):
        try:
            session = Session()
            print(f"{self.bill_id}")
            bill = BillInfo.get_bill_by_id(self.bill_id)
            print(f"bill Info: {bill}")
            
            if not bill:
                Messagebox.show_error("Bill not found", parent=self)
                return

            # Load shop information
            shop = ShopProfile.get_shop_info(bill.shop_id)
            print(f"Shop Info: {shop}")
            shop_info = f"{shop.shop_name} ({shop.shop_no})" if shop else "N/A"
            
            # Set basic info
            self.shop_info.config(text=shop_info)
            self.bill_date.config(text=bill.bill_date.strftime("%Y-%m-%d"))
            self.bill_period.config(text=f"{bill.bill_month}/{bill.bill_year}")
            self.total_amount.config(text=f"৳{bill.bill_amount:.2f}")
            if(bill.prev_due):
                self.prev_due.config(text=f"৳{bill.prev_due:.2f}")
            self.status.config(text="Paid" if bill.status == 2 else "Pending")

            # Load particulars
            particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
            
            print(f"particulars: {particulars}")
            
            for particular in particulars:
                self.particulars_tree.insert("", "end", values=(
                    particular.bill_particular,
                    particular.bill_qty,
                    particular.bill_unit,
                    f"৳{particular.bill_rate:.2f}",
                    f"৳{particular.sub_amount:.2f}"
                ))

            session.close()
            
        except Exception as e:
            print(f"Error loading bill: {str(e)}")
            Messagebox.show_error(f"Error loading bill: {str(e)}", parent=self)


    # def print_bill(self):
    #     session = Session()  # From utils.database
    #     try:
    #         # Fetch bill data by ID
    #         self.bill_data = session.query(BillInfo).filter_by(id=self.bill_id).first()
    #         if not self.bill_data:
    #             raise ValueError(f"Bill with ID {self.bill_id} not found")

    #         # Fetch associated shop data
    #         shop = session.query(ShopProfile).filter_by(id=self.bill_data.shop_id).first()

    #         # Set file name for the PDF in Downloads directory
    #         downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    #         filename = os.path.join(downloads_path, f"bill_{shop}.pdf")
    #         # filename = os.path.join(downloads_path, f"{shop.shop_name}-{shop.floor_no}-{shop.shop_no}({self.bill_data.bill_month}/{self.bill_data.bill_year}).pdf")

    #         # Set up the PDF canvas
    #         c = canvas.Canvas(filename, pagesize=letter)
    #         width, height = letter
    #         y_position = height - 40  # Start near the top of the page

    #         # Header
    #         c.setFont("Helvetica-Bold", 16)
    #         c.drawString(50, y_position, "GLOBAL CITY MANAGEMENT")
    #         y_position -= 30

    #         # Shop Info
    #         c.setFont("Courier-Bold", 12)
    #         if shop:
    #             c.drawString(50, y_position, f"{shop.shop_name}")
    #             y_position -= 15
    #             c.drawString(50, y_position, f"Floor {shop.floor_no}, Shop {shop.shop_no}")
    #             y_position -= 30
    #         else:
    #             c.drawString(50, y_position, "Shop Info: N/A")
    #             y_position -= 30

    #         # Bill Metadata
    #         c.setFont("Helvetica-Bold", 12)
    #         c.drawString(50, y_position, "Bill Information")
    #         y_position -= 20
    #         c.setFont("Courier", 10)
    #         bill_info = [
    #             ("Bill Date:", self.bill_data.bill_date.strftime("%Y-%m-%d") if self.bill_data.bill_date else "N/A"),
    #             ("Billing Period:", f"{self.bill_data.bill_month}/{self.bill_data.bill_year}"),
    #             ("Status:", "Paid" if self.bill_data.status == 2 else "Pending")
    #         ]
    #         for label, value in bill_info:
    #             c.drawString(60, y_position, f"{label} {value}")
    #             y_position -= 15

    #         # Description of Goods (Bill Particulars)
    #         c.setFont("Helvetica-Bold", 12)
    #         c.drawString(50, y_position, "Billing Descriotion")
    #         y_position -= 15
    #         c.setFont("Courier", 10)

    #         particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
    #         if particulars:
    #             for i, particular in enumerate(particulars):
    #                 line = f"{i+1}. {particular.bill_particular} - Qty: {particular.bill_qty} {particular.bill_unit}"
    #                 c.drawString(60, y_position, line)
    #                 y_position -= 15
    #                 c.drawString(70, y_position, f"Rate: ৳{particular.bill_rate:.2f} | Subtotal: ৳{particular.sub_amount:.2f}")
    #                 y_position -= 20
    #         else:
    #             c.drawString(60, y_position, "No particulars found")
    #             y_position -= 20

    #         # Electricity Section (Optional)
    #         c.setFont("Helvetica-Bold", 12)
    #         c.drawString(50, y_position, "Bill Calculations")
    #         y_position -= 20
    #         c.setFont("Courier", 10)
    #         elect_items = [
    #             ("Opening Units:", self.bill_data.elect_op_unit),
    #             ("Closing Units:", self.bill_data.elect_closing_unit),
    #             ("Demand Charge:", shop.elect_demand_chrge if shop else 0),
    #         ]
    #         for label, value in elect_items:
    #             c.drawString(60, y_position, f"{label} {value if value else 'N/A'}")
    #             y_position -= 15

    #         # Gas Section (Optional)
    #         gas_items = [
    #             ("Gas Opening:", self.bill_data.gas_op_unit),
    #             ("Gas Closing:", self.bill_data.gas_closing_unit),
    #         ]
    #         for label, value in gas_items:
    #             c.drawString(60, y_position, f"{label} {value if value else 'N/A'}")
    #             y_position -= 15

    #         # Financial Summary
    #         c.setFont("Helvetica-Bold", 12)
    #         c.drawString(50, y_position, "Shop Charge")
    #         y_position -= 20
    #         c.setFont("Courier", 10)
    #         financials = [
    #             ("Rent Amount:", f"৳{shop.rent_amount:.2f}" if shop and shop.rent_amount is not None else "N/A"),
    #             ("Previous Due:", f"৳{self.bill_data.prev_due:.2f}" if self.bill_data.prev_due is not None else "N/A"),
    #             ("Current Charges:", f"৳{self.bill_data.bill_amount:.2f}" if self.bill_data.bill_amount is not None else "N/A"),
    #             ("Total Payable:", f"৳{self.bill_data.cur_due:.2f}" if self.bill_data.cur_due is not None else "N/A"),
    #         ]
    #         for label, value in financials:
    #             c.drawString(60, y_position, label)
    #             c.drawString(200, y_position, value)
    #             y_position -= 15

    #         # Payment Info
    #         y_position -= 10
    #         c.setFont("Helvetica-Bold", 10)
    #         c.drawString(50, y_position, "Payment Details:")
    #         y_position -= 15
    #         c.setFont("Courier", 9)
    #         c.drawString(60, y_position, f"Last Payment Date: {self.bill_data.last_pay_date.strftime('%Y-%m-%d') if self.bill_data.last_pay_date else 'N/A'}")
    #         y_position -= 15
            
    #         pay_amount = f"৳{self.bill_data.pay_amount:.2f}" if self.bill_data.pay_amount is not None else "N/A"
    #         c.drawString(60, y_position, f"Last Payment Amount: {pay_amount}")


    #         # Footer
    #         y_position -= 30
    #         c.setFont("Helvetica-Oblique", 8)
    #         c.drawString(50, y_position, f"Generated by {self.bill_data.bill_gen_by} on {self.bill_data.bill_gen_at.strftime('%Y-%m-%d %H:%M') if self.bill_data.bill_gen_at else 'N/A'}")

    #         # Save and close the PDF
    #         c.save()

    #         # Open the generated PDF
    #         subprocess.run(["open", filename])  # macOS specific

            
    #         Messagebox.show_info(f"PDF saved to Downloads:\n{filename}", "Print Success")

    #     except Exception as e:
    #         # Handle any errors during the process
    #         print(f"Print failed: {str(e)}")
    #         Messagebox.show_error(f"Print failed: {str(e)}", parent=self)

    #     finally:
    #         # Always close the session
    #         session.close()
            
   
    # Particular mixxed table
    # def print_bill(self):
    #     session = Session()
    #     try:
    #         self.bill_data = session.query(BillInfo).filter_by(id=self.bill_id).first()
    #         if not self.bill_data:
    #             raise ValueError(f"Bill with ID {self.bill_id} not found")

    #         shop = session.query(ShopProfile).filter_by(id=self.bill_data.shop_id).first()
    #         downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    #         filename = os.path.join(downloads_path, f"bill_{shop.shop_no}.pdf")

    #         pdf = FPDF()
    #         pdf.add_page()
    #         pdf.set_auto_page_break(auto=True, margin=15)
    #         font_path = os.path.join("fonts", "NotoSansBengali-Regular.ttf")
    #         pdf.add_font("Noto", "", font_path, uni=True)

    #         # Header
    #         pdf.set_font("Noto", "", 16)
    #         pdf.cell(0, 10, "GLOBAL CITY MANAGEMENT", ln=True, align="C")

    #         # Shop Info
    #         pdf.set_font("Courier", "", 12)
    #         if shop:
    #             pdf.cell(0, 10, f"{shop.shop_name}", ln=True)
    #             pdf.cell(0, 10, f"Floor {shop.floor_no}, Shop {shop.shop_no}", ln=True)
    #         else:
    #             pdf.cell(0, 10, "Shop Info: N/A", ln=True)

    #         # Bill Metadata
    #         pdf.set_font("Noto", "", 12)
    #         pdf.cell(0, 10, "Bill Information", ln=True)

    #         pdf.set_font("Courier", "", 10)
    #         bill_info = [
    #             ("Bill Date:", self.bill_data.bill_date.strftime("%Y-%m-%d") if self.bill_data.bill_date else "N/A"),
    #             ("Billing Period:", f"{self.bill_data.bill_month}/{self.bill_data.bill_year}"),
    #             ("Status:", "Paid" if self.bill_data.status == 2 else "Pending")
    #         ]
    #         for label, value in bill_info:
    #             pdf.cell(0, 8, f"{label} {value}", ln=True)

    #         # Billing Description
    #         pdf.set_font("Noto", "", 12)
    #         pdf.cell(0, 10, "Billing Description", ln=True)
    #         pdf.set_font("Noto", "", 10)

    #         # Table Headers
    #         pdf.set_fill_color(200, 200, 200)
    #         pdf.cell(10, 8, "No", border=1, align="C", fill=True)
    #         pdf.cell(70, 8, "Particular", border=1, align="L", fill=True)
    #         pdf.cell(20, 8, "Qty", border=1, align="C", fill=True)
    #         pdf.cell(30, 8, "Rate (৳)", border=1, align="R", fill=True)
    #         pdf.cell(30, 8, "Subtotal (৳)", border=1, align="R", fill=True)
    #         pdf.ln()

    #         # Table Rows
    #         particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
    #         if particulars:
    #             for i, p in enumerate(particulars, start=1):
    #                 pdf.cell(10, 8, str(i), border=1, align="C")
    #                 pdf.cell(70, 8, p.bill_particular, border=1)
    #                 qty_unit = f"{p.bill_qty} {p.bill_unit}"
    #                 pdf.cell(20, 8, qty_unit, border=1, align="C")
    #                 pdf.cell(30, 8, f"{p.bill_rate:.2f}", border=1, align="R")
    #                 pdf.cell(30, 8, f"{p.sub_amount:.2f}", border=1, align="R")
    #                 pdf.ln()
    #         else:
    #             pdf.cell(0, 8, "No particulars found", ln=True)

    #         # Billing Description
    #         # pdf.set_font("Noto", "", 12)
    #         # pdf.cell(0, 10, "Billing Description", ln=True)
    #         # pdf.set_font("Courier", "", 10)

    #         # particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
    #         # if particulars:
    #         #     for i, p in enumerate(particulars):
    #         #         pdf.cell(0, 8, f"{i+1}. {p.bill_particular} - Qty: {p.bill_qty} {p.bill_unit}", ln=True)
    #         #         pdf.cell(0, 8, f"    Rate: {p.bill_rate:.2f}BDT | Subtotal: {p.sub_amount:.2f}BDT", ln=True)
    #         # else:
    #         #     pdf.cell(0, 8, "No particulars found", ln=True)

    #         # Electricity Section
    #         # pdf.set_font("Noto", "", 12)
    #         # pdf.cell(0, 10, "Bill Calculations", ln=True)
    #         # pdf.set_font("Courier", "", 10)
    #         # elect_items = [
    #         #     ("Opening Units:", self.bill_data.elect_op_unit),
    #         #     ("Closing Units:", self.bill_data.elect_closing_unit),
    #         #     ("Demand Charge:", shop.elect_demand_chrge if shop else 0),
    #         # ]
    #         # for label, value in elect_items:
    #         #     pdf.cell(0, 8, f"{label} {value if value else 'N/A'}", ln=True)
                
    #         # Electricity + Gas + Financial Summary + Payment Table (Unified Table)
    #         pdf.ln(5)
    #         pdf.set_font("Noto", "", 12)
    #         pdf.cell(0, 10, "Bill Summary", ln=True)

    #         pdf.set_font("Noto", "", 10)
    #         pdf.set_fill_color(230, 230, 230)

    #         # Table Header
    #         pdf.cell(70, 8, "Description", border=1, fill=True)
    #         pdf.cell(0, 8, "Value", border=1, fill=True)
    #         pdf.ln()

    #         def add_row(label, value):
    #             value_text = str(value if value is not None else "N/A")
    #             pdf.cell(70, 8, label, border=1)
    #             pdf.cell(0, 8, value_text, border=1)
    #             pdf.ln()

    #         # Metadata
    #         add_row("Bill Date", self.bill_data.bill_date.strftime("%Y-%m-%d") if self.bill_data.bill_date else "N/A")
    #         add_row("Billing Period", f"{self.bill_data.bill_month}/{self.bill_data.bill_year}")
    #         add_row("Status", "Paid" if self.bill_data.status == 2 else "Pending")

    #         # Electricity
    #         add_row("Electricity Opening Unit", self.bill_data.elect_op_unit)
    #         add_row("Electricity Closing Unit", self.bill_data.elect_closing_unit)
    #         add_row("Electricity Demand Charge", shop.elect_demand_chrge if shop else "N/A")

    #         # Gas
    #         add_row("Gas Opening Unit", self.bill_data.gas_op_unit)
    #         add_row("Gas Closing Unit", self.bill_data.gas_closing_unit)

    #         # Financials
    #         add_row("Rent Amount", f"{shop.rent_amount:.2f} BDT" if shop and shop.rent_amount is not None else "N/A")
    #         add_row("Previous Due", f"{self.bill_data.prev_due:.2f} BDT" if self.bill_data.prev_due is not None else "N/A")
    #         add_row("Current Charges", f"{self.bill_data.bill_amount:.2f} BDT" if self.bill_data.bill_amount is not None else "N/A")
    #         add_row("Total Payable", f"{self.bill_data.cur_due:.2f} BDT" if self.bill_data.cur_due is not None else "N/A")

    #         # Payment Info
    #         add_row("Last Payment Date", self.bill_data.last_pay_date.strftime("%Y-%m-%d") if self.bill_data.last_pay_date else "N/A")
    #         add_row("Last Payment Amount", f"{self.bill_data.pay_amount:.2f} BDT" if self.bill_data.pay_amount is not None else "N/A")


    #         # Gas Section
    #         gas_items = [
    #             ("Gas Opening:", self.bill_data.gas_op_unit),
    #             ("Gas Closing:", self.bill_data.gas_closing_unit),
    #         ]
    #         for label, value in gas_items:
    #             pdf.cell(0, 8, f"{label} {value if value else 'N/A'}", ln=True)

    #         # Financial Summary
    #         # pdf.set_font("Noto", "B", 12)
            
    #         pdf.cell(0, 10, "Shop Charge", ln=True)
    #         pdf.set_font("Courier", "", 10)
    #         financials = [
    #             ("Rent Amount:", f"{shop.rent_amount:.2f}BDT" if shop and shop.rent_amount is not None else "N/A"),
    #             ("Previous Due:", f"{self.bill_data.prev_due:.2f}BDT" if self.bill_data.prev_due is not None else "N/A"),
    #             ("Current Charges:", f"{self.bill_data.bill_amount:.2f}BDT" if self.bill_data.bill_amount is not None else "N/A"),
    #             ("Total Payable:", f"{self.bill_data.cur_due:.2f}BDT" if self.bill_data.cur_due is not None else "N/A"),
    #         ]
    #         for label, value in financials:
    #             pdf.cell(80, 8, label, ln=False)
    #             pdf.cell(0, 8, value, ln=True)

    #         # Payment Info
    #         pdf.set_font("Noto", "", 10)
    #         pdf.cell(0, 10, "Payment Details:", ln=True)
    #         pdf.set_font("Courier", "", 9)
    #         pdf.cell(0, 8, f"Last Payment Date: {self.bill_data.last_pay_date.strftime('%Y-%m-%d') if self.bill_data.last_pay_date else 'N/A'}", ln=True)
    #         pay_amount = f"{self.bill_data.pay_amount:.2f}BDT" if self.bill_data.pay_amount is not None else "N/A"
    #         pdf.cell(0, 8, f"Last Payment Amount: {pay_amount}", ln=True)

    #         # Footer
    #         pdf.set_font("Noto", "", 8)
    #         pdf.ln(10)
    #         pdf.cell(0, 8, f"Generated by {self.bill_data.bill_gen_by} on {self.bill_data.bill_gen_at.strftime('%Y-%m-%d %H:%M') if self.bill_data.bill_gen_at else 'N/A'}", ln=True)

    #         # Save PDF
    #         pdf.output(filename)

    #         # Open the PDF (platform-specific)
    #         if os.name == 'posix':
    #             subprocess.run(['open', filename])  # macOS
    #         elif os.name == 'nt':
    #             os.startfile(filename)  # Windows
    #         else:
    #             subprocess.run(['xdg-open', filename])  # Linux

    #         showinfo("Print Success", f"PDF saved to Downloads:\n{filename}")

    #     except Exception as e:
    #         print(f"Print failed: {str(e)}")
    #         showerror("Print Failed", f"Error: {str(e)}")

    #     finally:
    #         session.close()
            
    def print_bill(self):
        session = Session()
        try:
            self.bill_data = session.query(BillInfo).filter_by(id=self.bill_id).first()
            if not self.bill_data:
                raise ValueError(f"Bill with ID {self.bill_id} not found")

            shop = session.query(ShopProfile).filter_by(id=self.bill_data.shop_id).first()
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = os.path.join(downloads_path, f"bill_{shop.shop_no}.pdf")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            font_path = os.path.join("fonts", "NotoSansBengali-Regular.ttf")
            pdf.add_font("Noto", "", font_path, uni=True)

            # Header
            pdf.set_font("Noto", "", 16)
            pdf.cell(0, 10, "GLOBAL CITY MANAGEMENT", ln=True, align="C")
            pdf.set_font("Noto", "", 8)
            pdf.cell(0, 5, "Bali Arcade, 227, Nawab Serajuddawla Road, Chwakbazar, Chattogram", ln=True, align="C")

            # Setup font
            pdf.set_font("Courier", "", 10)

            # Setup data
            left_column = [
                f"{shop.shop_name}" if shop else "Shop Info: N/A",
                f"Floor {shop.floor_no}, Shop {shop.shop_no}" if shop else ""
            ]

            right_column = [
                ("Bill Date:", self.bill_data.bill_date.strftime("%Y-%m-%d") if self.bill_data.bill_date else "N/A"),
                ("Billing Period:", f"{self.bill_data.bill_month}/{self.bill_data.bill_year}"),
                ("Status:", "Paid" if self.bill_data.status == 2 else "Pending")
            ]

            # Ensure the columns have the same number of lines
            max_lines = max(len(left_column), len(right_column))
            while len(left_column) < max_lines:
                left_column.append("")
            while len(right_column) < max_lines:
                right_column.append(("", ""))

            # Column widths
            left_col_width = 90
            right_label_width = 30
            right_value_width = 70

            # Draw rows
            for i in range(max_lines):
                # Bold only for first line (shop name)
                if i == 0:
                    pdf.set_font("Courier", "B", 10)
                else:
                    pdf.set_font("Courier", "", 10)

                pdf.cell(left_col_width, 8, left_column[i], border=0)

                # Right side (always regular)
                label, value = right_column[i]
                pdf.set_font("Courier", "", 10)
                pdf.cell(right_label_width, 8, label, border=0)
                pdf.cell(right_value_width, 8, value, border=0, ln=True)



            # Summary Table (4-column format)
            pdf.ln(5)
            pdf.set_font("Noto", "", 12)
            pdf.cell(0, 10, "Bill Summary", ln=True, align="C")
            pdf.set_font("Noto", "", 10)

            def add_summary_row(label1, value1, label2, value2):
                val1 = str(value1 if value1 is not None else "N/A")
                val2 = str(value2 if value2 is not None else "N/A")
                pdf.cell(50, 8, label1, border=0)
                pdf.cell(45, 8, val1, border=0)
                pdf.cell(50, 8, label2, border=0)
                pdf.cell(45, 8, val2, border=0)
                pdf.ln()

            add_summary_row("Bill Date:", self.bill_data.bill_date.strftime("%Y-%m-%d") if self.bill_data.bill_date else "N/A",
                            "Billing Period:", f"{self.bill_data.bill_month}/{self.bill_data.bill_year}")
            add_summary_row("Status:", "Paid" if self.bill_data.status == 2 else "Pending",
                            "Electricity Op:", self.bill_data.elect_op_unit)
            add_summary_row("Electricity Cl:", self.bill_data.elect_closing_unit,
                            "Demand Charge:", shop.elect_demand_chrge if shop else "N/A")
            add_summary_row("Gas Opening:", self.bill_data.gas_op_unit,
                            "Gas Closing:", self.bill_data.gas_closing_unit)
            add_summary_row("Rent Amount:", f"{shop.rent_amount:.2f} BDT" if shop and shop.rent_amount else "N/A",
                            "Previous Due:", f"{self.bill_data.prev_due:.2f} BDT" if self.bill_data.prev_due else "N/A")
            add_summary_row("Current Charges:", f"{self.bill_data.bill_amount:.2f} BDT" if self.bill_data.bill_amount else "N/A",
                            "Total Payable:", f"{self.bill_data.cur_due:.2f} BDT" if self.bill_data.cur_due else "N/A")
            add_summary_row("Last Pay Date:", self.bill_data.last_pay_date.strftime("%Y-%m-%d") if self.bill_data.last_pay_date else "N/A",
                            "Last Pay Amount:", f"{self.bill_data.pay_amount:.2f} BDT" if self.bill_data.pay_amount else "N/A")

            # Billing Description Table
            # pdf.set_font("Noto", "", 12)
            # pdf.cell(0, 10, "Billing Description", ln=True)
            # pdf.set_font("Noto", "", 10)

            pdf.set_font("Noto", "", 10)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(10, 8, "No", border=1, align="C", fill=True)
            pdf.cell(70, 8, "Particular", border=1, align="L", fill=True)
            pdf.cell(20, 8, "Qty", border=1, align="C", fill=True)
            pdf.cell(30, 8, "Rate (৳)", border=1, align="R", fill=True)
            pdf.cell(30, 8, "Subtotal (৳)", border=1, align="R", fill=True)
            pdf.ln()

            particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
            grand_total = 0.0

            if particulars:
                for i, p in enumerate(particulars, start=1):
                    pdf.cell(10, 8, str(i), border=1, align="C")
                    pdf.cell(70, 8, p.bill_particular, border=1)
                    qty_unit = f"{p.bill_qty} {p.bill_unit}"
                    pdf.cell(20, 8, qty_unit, border=1, align="C")
                    pdf.cell(30, 8, f"{p.bill_rate:.2f}", border=1, align="R")
                    pdf.cell(30, 8, f"{ float(p.bill_qty) * float(p.bill_rate):.2f}", border=1, align="R")
                    pdf.ln()
                    grand_total += float(p.bill_qty) * float(p.bill_rate)

                # Grand Total row
                pdf.set_font("Noto", "", 10)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(130, 8, "Grand Total", border=1, align="R", fill=True)
                pdf.cell(30, 8, f"{grand_total:.2f}", border=1, align="R", fill=True)
                pdf.ln()

            else:
                pdf.cell(0, 8, "No particulars found", ln=True)

                
            # Footer
            pdf.set_font("Noto", "", 8)
            pdf.ln(10)
            pdf.cell(0, 8, f"Generated by {self.bill_data.bill_gen_by} on {self.bill_data.bill_gen_at.strftime('%Y-%m-%d %H:%M') if self.bill_data.bill_gen_at else 'N/A'}", ln=True)

            # Save PDF
            pdf.output(filename)

            # Open the PDF (platform-specific)
            if os.name == 'posix':
                subprocess.run(['open', filename])  # macOS
            elif os.name == 'nt':
                os.startfile(filename)  # Windows
            else:
                subprocess.run(['xdg-open', filename])  # Linux

            showinfo("Print Success", f"PDF saved to Downloads:\n{filename}")

        except Exception as e:
            print(f"Print failed: {str(e)}")
            showerror("Print Failed", f"Error: {str(e)}")

        finally:
            session.close()


            
    def create_hello_pdf(self):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        filename = os.path.join(downloads_path, "hello_world.pdf")

        c = canvas.Canvas(filename)
        c.setFont("Helvetica", 20)
        c.drawString(100, 750, "Hello, World!")
        c.save()

        print(f"PDF saved to: {filename}")


    # Usage example - in your list view class:
    def show_bill_detail(self, event=None):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Please select a bill", parent=self)
            return
        
        bill_id = self.tree.item(selected[0])['values'][0]
        detail_window = ttk.Toplevel(self)
        detail_window.title("Bill Details")
        detail_window.geometry("800x600")
        
        BillDetailView(detail_window, bill_id).pack(fill="both", expand=True)
        
        
# class PDF(FPDF):
#     def header(self):
#         self.set_font("Noto", size=16)
#         self.cell(0, 10, "GLOBAL CITY MANAGEMENT", ln=True, align="C")
