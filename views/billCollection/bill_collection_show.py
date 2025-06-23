     
    
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.bill_info import BillInfo
from models.bill_particular import BillParticular
from models.shop_profile import ShopProfile
from models.bill_collection import BillCollection
from utils.database import Session
from tkinter.messagebox import showinfo, showerror

# PDF GENERATION
import os
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from fpdf import FPDF

class BillCollectionShowView(ttk.Frame):
    def __init__(self, parent, collection_id):
        super().__init__(parent, padding=20)
        self.collection_id = collection_id
        self.parent = parent
        self.style = ttk.Style()

        self.configure_styles()
        self.create_widgets()
        self.load_collection_data()

    def configure_styles(self):
        self.style.configure("TFrame", background="white")
        self.style.configure("TLabel", background="white", font=("Helvetica", 10))
        self.style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=10)

        self.title_label = ttk.Label(
            header_frame,
            text="Bill  Collection Details",
            style="Title.TLabel",
            bootstyle=PRIMARY
        )
        self.title_label.pack(side="left")

        ttk.Button(
            header_frame,
            text="Print Bill Collection",
            command=self.print_bill,
            bootstyle=INFO,
            width=15
        ).pack(side="right", padx=10)

        info_frame = ttk.LabelFrame(main_frame, text="Bill Collection Information", padding=10)
        info_frame.pack(fill="x", pady=10)

        self.create_info_rows(info_frame)

        particulars_frame = ttk.LabelFrame(main_frame, text="Bill Collection Particulars", padding=10)
        particulars_frame.pack(fill="both", expand=True, pady=10)

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

        for i in range(0, len(rows), 2):
            frame = ttk.Frame(parent)
            frame.pack(fill="x", pady=2)

            label_text1, var_name1 = rows[i]
            ttk.Label(frame, text=label_text1, width=15, style="Header.TLabel").pack(side=LEFT)
            setattr(self, var_name1, ttk.Label(frame, text="", width=20))
            getattr(self, var_name1).pack(side=LEFT, padx=(0, 20))

            if i + 1 < len(rows):
                label_text2, var_name2 = rows[i + 1]
                ttk.Label(frame, text=label_text2, width=15, style="Header.TLabel").pack(side=LEFT)
                setattr(self, var_name2, ttk.Label(frame, text="", width=20))
                getattr(self, var_name2).pack(side=LEFT)

    def load_collection_data(self):
        try:
            session = Session()

            result = (
                session.query(
                    BillCollection,
                    BillInfo.bill_month,
                    BillInfo.bill_year,
                    BillInfo.bill_date,
                    BillInfo.bill_amount,
                    BillInfo.prev_due,
                    BillInfo.status,
                    BillInfo.owner_id
                )
                .join(BillInfo, BillInfo.id == BillCollection.bill_id)
                .filter(BillCollection.id == self.collection_id)
                .first()
            )

            if not result:
                Messagebox.show_error("Bill Collection not found", parent=self)
                return

            collection, bill_month, bill_year, bill_date, bill_amount, prev_due, status, owner_id = result

            shop = ShopProfile.get_shop_info(collection.shop_id)
            shop_info = f"{shop.shop_name} ({shop.shop_no})" if shop else "N/A"

            self.shop_info.config(text=shop_info)
            self.bill_date.config(text=bill_date.strftime("%Y-%m-%d") if bill_date else "N/A")
            self.bill_period.config(text=f"{bill_month}/{bill_year}" if bill_month and bill_year else "N/A")
            self.bill_month.config(text=str(bill_month) if bill_month else "")
            self.bill_year.config(text=str(bill_year) if bill_year else "")
            self.total_amount.config(text=f"৳{bill_amount:.2f}" if bill_amount else "৳0.00")
            self.prev_due.config(text=f"৳{prev_due:.2f}" if prev_due else "৳0.00")
            self.status.config(text="Paid" if status == 2 else "Pending")

            particulars = session.query(BillParticular).filter_by(bill_collection_id=self.collection_id).all()
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

    def print_bill(self):
        session = Session()
        try:
            # Fetch collection with bill info
            result = (
                session.query(
                    BillCollection,
                    BillInfo,
                    ShopProfile
                )
                .join(BillInfo, BillInfo.id == BillCollection.bill_id)
                .join(ShopProfile, ShopProfile.id == BillCollection.shop_id)
                .filter(BillCollection.id == self.collection_id)
                .first()
            )

            if not result:
                raise ValueError(f"Collection ID {self.collection_id} not found")

            collection, bill_info, shop = result

            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = os.path.join(downloads_path, f"bill_collection_{shop.shop_no}.pdf")

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
            pdf.ln(5)

            # Shop & Bill Info
            pdf.set_font("Courier", "", 10)
            left = [
                f"{shop.shop_name}",
                f"Floor {shop.floor_no}, Shop {shop.shop_no}"
            ]
            right = [
                ("Bill Date:", bill_info.bill_date.strftime("%Y-%m-%d") if bill_info.bill_date else "N/A"),
                ("Period:", f"{bill_info.bill_month}/{bill_info.bill_year}"),
                ("Status:", "Paid" if bill_info.status == 2 else "Pending")
            ]

            for i in range(max(len(left), len(right))):
                pdf.set_font("Courier", "B" if i == 0 else "", 10)
                pdf.cell(90, 8, left[i] if i < len(left) else "", border=0)
                label, val = right[i] if i < len(right) else ("", "")
                pdf.set_font("Courier", "", 10)
                pdf.cell(30, 8, label, border=0)
                pdf.cell(60, 8, val, border=0, ln=True)

            # Summary
            pdf.ln(5)
            pdf.set_font("Noto", "", 12)
            pdf.cell(0, 10, "Collection Summary", ln=True, align="C")
            pdf.set_font("Noto", "", 10)

            def summary_row(label1, val1, label2, val2):
                pdf.cell(50, 8, label1, border=0)
                pdf.cell(45, 8, str(val1 or "N/A"), border=0)
                pdf.cell(50, 8, label2, border=0)
                pdf.cell(45, 8, str(val2 or "N/A"), border=0)
                pdf.ln()

            summary_row("Total Amount:", f"৳{bill_info.bill_amount:.2f}", "Previous Due:", f"৳{bill_info.prev_due:.2f}")
            summary_row("Status:", "Paid" if bill_info.status == 2 else "Pending", "", "")

            # Particulars Table
            pdf.ln(5)
            pdf.set_font("Noto", "", 10)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(10, 8, "No", border=1, align="C", fill=True)
            pdf.cell(70, 8, "Particular", border=1, align="L", fill=True)
            pdf.cell(20, 8, "Qty", border=1, align="C", fill=True)
            pdf.cell(30, 8, "Rate (৳)", border=1, align="R", fill=True)
            pdf.cell(30, 8, "Subtotal (৳)", border=1, align="R", fill=True)
            pdf.ln()

            particulars = session.query(BillParticular).filter_by(bill_collection_id=self.collection_id).all()
            grand_total = 0.0

            if particulars:
                for i, p in enumerate(particulars, start=1):
                    subtotal = float(p.bill_qty) * float(p.bill_rate)
                    grand_total += subtotal

                    pdf.cell(10, 8, str(i), border=1, align="C")
                    pdf.cell(70, 8, p.bill_particular, border=1)
                    pdf.cell(20, 8, f"{p.bill_qty} {p.bill_unit}", border=1, align="C")
                    pdf.cell(30, 8, f"{p.bill_rate:.2f}", border=1, align="R")
                    pdf.cell(30, 8, f"{subtotal:.2f}", border=1, align="R")
                    pdf.ln()

                # Total
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(130, 8, "Grand Total", border=1, align="R", fill=True)
                pdf.cell(30, 8, f"{grand_total:.2f}", border=1, align="R", fill=True)
                pdf.ln()
            else:
                pdf.cell(0, 8, "No particulars found.", ln=True)

            # Footer
            pdf.ln(10)
            pdf.set_font("Noto", "", 8)
            pdf.cell(0, 8, f"Generated by {bill_info.bill_gen_by or 'N/A'} on {bill_info.bill_gen_at.strftime('%Y-%m-%d %H:%M') if bill_info.bill_gen_at else 'N/A'}", ln=True)

            # Save PDF
            pdf.output(filename)

            # Open PDF
            if os.name == 'posix':
                subprocess.run(['open', filename])
            elif os.name == 'nt':
                os.startfile(filename)
            else:
                subprocess.run(['xdg-open', filename])

            showinfo("Print Success", f"PDF saved to Downloads:\n{filename}")

        except Exception as e:
            print(f"Print failed: {str(e)}")
            showerror("Print Failed", f"Error: {str(e)}")

        finally:
            session.close()


