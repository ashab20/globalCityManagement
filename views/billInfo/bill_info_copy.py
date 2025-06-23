# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *
# from ttkbootstrap.dialogs import Messagebox
# from models.bill_info import BillInfo
# from models.bill_particular import BillParticular
# from models.shop_profile import ShopProfile
# from utils.database import Session
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.platypus import Paragraph
# from datetime import datetime

# class BillDetailView(ttk.Frame):
#     def __init__(self, parent, bill_id):
#         super().__init__(parent, padding=20)
#         self.bill_id = bill_id
#         self.parent = parent
#         self.style = ttk.Style()
#         self.bill_data = None
        
#         self.configure_styles()
#         self.create_widgets()
#         self.load_bill_data()
    

#     def configure_styles(self):
#         self.style.configure("TFrame", background="white")
#         self.style.configure("TLabel", background="white", font=("Courier New", 10))
#         self.style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
#         self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
#         self.style.configure("Fixed.TLabel", font=("Courier New", 10))

#     def create_widgets(self):
#         main_frame = ttk.Frame(self, bootstyle="light")
#         main_frame.pack(fill="both", expand=True, padx=20, pady=20)

#         # Header Section
#         header_frame = ttk.Frame(main_frame)
#         header_frame.pack(fill="x", pady=10)
        
#         ttk.Label(
#             header_frame,
#             text="GLOBAL CITY MANAGEMENT",
#             font=("Helvetica", 16, "bold"),
#             bootstyle="primary"
#         ).pack(side=LEFT)

#         ttk.Button(
#             header_frame,
#             text="Print Bill",
#             command=self.print_bill,
#             bootstyle="info",
#             width=15
#         ).pack(side=RIGHT)

#         # Party Details
#         self.party_label = ttk.Label(
#             main_frame,
#             text="",
#             font=("Courier New", 10)
#         )
#         self.party_label.pack(fill="x", pady=5, anchor=W)

#         # Description of Goods
#         desc_frame = ttk.Frame(main_frame)
#         desc_frame.pack(fill="x", pady=10, anchor=W)
#         ttk.Label(
#             desc_frame,
#             text="Description of Goods",
#             font=("Helvetica", 12, "bold")
#         ).pack(anchor=W)
        
#         self.desc_items_frame = ttk.Frame(desc_frame)
#         self.desc_items_frame.pack(anchor=W)

#         # # Acknowledgment Section
#         # ack_frame = ttk.Frame(main_frame)
#         # ack_frame.pack(fill="x", pady=10, anchor=W)
#         # ttk.Label(
#         #     ack_frame,
#         #     text="Acknowledgment",
#         #     font=("Helvetica", 12, "bold")
#         # ).pack(anchor=W)
        
#         # self.gross_units_frame = ttk.Frame(ack_frame)
#         # self.gross_units_frame.pack(anchor=W, padx=20)

#         # # Other Items Section
#         # other_frame = ttk.Frame(main_frame)
#         # other_frame.pack(fill="x", pady=10, anchor=W)
#         # ttk.Label(
#         #     other_frame,
#         #     text="Other Items: charged fees",
#         #     font=("Helvetica", 12, "bold")
#         # ).pack(anchor=W)
        
#         # self.legend_frame = ttk.Frame(other_frame)
#         # self.legend_frame.pack(anchor=W, padx=20)

#         # Totals Section
#         totals_frame = ttk.Frame(main_frame)
#         totals_frame.pack(fill="x", pady=10)
        
#         self.totals_labels = {
#             "total": ttk.Label(totals_frame, font=("Courier New", 10)),
#             "amount": ttk.Label(totals_frame, font=("Courier New", 10)),
#             "cost": ttk.Label(totals_frame, font=("Courier New", 10)),
#             "": ttk.Label(totals_frame, font=("Courier New", 10)),
#             "time_points": ttk.Label(totals_frame, font=("Courier New", 10))
#         }
        
#         for i, (key, label) in enumerate(self.totals_labels.items()):
#             label.grid(row=i, column=1, sticky=E)
            
#         totals_frame.columnconfigure(0, weight=1)
#         totals_frame.columnconfigure(1, weight=1)

#     def load_bill_data(self):
#         try:
#             session = Session()
#             self.bill_data = session.query(BillInfo).filter_by(id=self.bill_id).first()
#             shop = session.query(ShopProfile).filter_by(id=self.bill_data.shop_id).first()

#             print(f"Bill Data: {self.bill_data}")
#             print(f"Bill Data: {shop}")
#             # Party Details
#             self.party_label.config(
#                 text=f"Party Details: Select Level {shop.floor_no}, {shop.shop_no} → Go_id"
#             )

#             # Description of Goods
#             particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
#             for widget in self.desc_items_frame.winfo_children():
#                 widget.destroy()
            
#             for i, particular in enumerate(particulars):
#                 ttk.Label(
#                     self.desc_items_frame,
#                     text=f"{i+1}. {particular.bill_particular}",
#                     style="Fixed.TLabel"
#                 ).pack(anchor=W)

#             # # Acknowledgment
#             # ttk.Label(self.gross_units_frame, text="Units:").pack(anchor=W)
#             # ttk.Label(self.gross_units_frame, 
#             #          text=f"${self.bill_data.gross_units:.2f} ST").pack(anchor=W)
#             # ttk.Label(self.gross_units_frame, 
#             #          text=f"${self.bill_data.unit_rate:.2f} PER UNI").pack(anchor=W)
#             # ttk.Label(self.gross_units_frame, 
#             #          text=f"${self.bill_data.kw_rate:.2f} per KW").pack(anchor=W)

#             # # Other Items
#             # ttk.Label(self.legend_frame, text="Fee:").pack(anchor=W)
#             # ttk.Label(self.legend_frame, 
#             #           text=f"£{self.bill_data.country_fee:.2f} Country").pack(anchor=W)
#             # ttk.Label(self.legend_frame, 
#             #           text=f"fees: £{self.bill_data.legal_fees:.2f}").pack(anchor=W)

#             # Totals
#             self.totals_labels["Bill Amount"].config(
#                 text=f"${self.bill_data.bill_amount:.2f} Units"
#             )
#             self.totals_labels["Payamount"].config(
#                 text=f"${self.bill_data.pay_amount:.2f}"
#             )
#             self.totals_labels["Due"].config(
#                 text=f"${self.bill_data.cur_due:.2f}"
#             )
#             # self.totals_labels[""].config(
#             #     text="\n".join([f"${amt:.2f}" for amt in self.bill_data.additional_signatory])
#             # )
#             # self.totals_labels["time_points"].config(
#             #     text="\n".join([f"${tp:.2f}" for tp in self.bill_data.bill_year])
#             # )

#             session.close()
            
#         except Exception as e:
#             Messagebox.show_error(f"Error loading bill: {str(e)}", parent=self)

#     def print_bill(self):
#         session = Session()
#         try:
#             filename = f"bill_{self.bill_id}.pdf"
#             c = canvas.Canvas(filename, pagesize=letter)
#             width, height = letter
#             y_position = height - 40
            
#             # Header
#             c.setFont("Helvetica-Bold", 16)
#             c.drawString(50, y_position, "GLOBAL CITY MANAGEMENT")
#             y_position -= 30

#             # Party Details
#             c.setFont("Courier", 10)
#             c.drawString(50, y_position, self.party_label.cget("text"))
#             y_position -= 20

#             # Description of Goods
#             c.setFont("Helvetica-Bold", 12)
#             c.drawString(50, y_position, "Description of Goods")
#             y_position -= 15
#             c.setFont("Courier", 10)
            
#             particulars = session.query(BillParticular).filter_by(bill_id=self.bill_id).all()
#             for i, particular in enumerate(particulars):
#                 c.drawString(60, y_position, f"{i+1}. {particular.description}")
#                 y_position -= 15

#             # Acknowledgment
#             y_position -= 10
#             c.setFont("Helvetica-Bold", 12)
#             c.drawString(50, y_position, "Acknowledgment")
#             y_position -= 15
#             c.setFont("Courier", 10)
#             c.drawString(70, y_position, "Gross Units:")
#             y_position -= 15
#             c.drawString(70, y_position, f"${self.bill_data.gross_units:.2f} ST")
#             y_position -= 15
#             c.drawString(70, y_position, f"${self.bill_data.unit_rate:.2f} PER UNI")
#             y_position -= 15
#             c.drawString(70, y_position, f"${self.bill_data.kw_rate:.2f} per KW")
#             y_position -= 20

#             # Other Items
#             c.setFont("Helvetica-Bold", 12)
#             c.drawString(50, y_position, "Other Items: charged fees")
#             y_position -= 15
#             c.setFont("Courier", 10)
#             c.drawString(70, y_position, "Legend Free:")
#             y_position -= 15
#             c.drawString(70, y_position, f"£{self.bill_data.country_fee:.2f} Country")
#             y_position -= 15
#             c.drawString(70, y_position, f"Legal fees: £{self.bill_data.legal_fees:.2f}")
#             y_position -= 20

#             # Totals
#             totals = [
#                 ("General Total:", f"${self.bill_data.general_total:.2f} Units"),
#                 ("Price: Amount(TM):", f"${self.bill_data.price_amount:.2f}"),
#                 ("Annual Cost:", f"${self.bill_data.annual_cost:.2f}"),
#                 ("Additional Signatory:", "\n".join([f"${amt:.2f}" for amt in self.bill_data.additional_signatory])),
#                 ("Time Points:", "\n".join([f"${tp:.2f}" for tp in self.bill_data.time_points]))
#             ]

#             c.setFont("Courier", 10)
#             for label, value in totals:
#                 c.drawString(50, y_position, label)
#                 text = c.beginText(200, y_position)
#                 text.textLines(value)
#                 c.drawText(text)
#                 y_position -= 15 * (value.count('\n') + 1)

#             c.save()
#             Messagebox.show_info(f"PDF saved as {filename}", "Print Success")
            
#         except Exception as e:
#             Messagebox.show_error(f"Print failed: {str(e)}", parent=self)

#     def show_bill_detail(self, event=None):
#         selected = self.tree.selection()
#         if not selected:
#             Messagebox.show_warning("Please select a bill", parent=self)
#             return
        
#         bill_id = self.tree.item(selected[0])['values'][0]
#         detail_window = ttk.Toplevel(self)
#         detail_window.title("Bill Details")
#         detail_window.geometry("800x600")
#         BillDetailView(detail_window, bill_id).pack(fill="both", expand=True)
        
        
   