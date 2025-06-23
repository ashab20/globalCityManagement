from ttkbootstrap import Frame, Style, Scrollbar, Button, Treeview, Toplevel
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.bill_collection import BillCollection
from utils.database import Session
from sqlalchemy.orm import joinedload
from models.shop_profile import ShopProfile
from models.bill_info import BillInfo
from models.BankAccount import BankAccount
from views.billCollection.bill_collection_show import BillCollectionShowView


class CollectionListView(Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent

        style = Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.create_collection_list()

    def create_collection_list(self):
        columns = ("ID", "Shop ID", "Bill ID", "Date", "Mode", "Amount", "Pay Amount", "Due Amount", "Bank ID", "Cheque No", "Remarks", "Edit", "Delete")
        self.tree = Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        for col in columns:
            self.tree.heading(col, text=col)

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Shop ID", width=80, anchor="center")
        self.tree.column("Bill ID", width=80, anchor="center")
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Mode", width=100, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Pay Amount", width=100, anchor="center")
        self.tree.column("Due Amount", width=100, anchor="center")
        self.tree.column("Bank ID", width=80, anchor="center")
        self.tree.column("Cheque No", width=100, anchor="center")
        self.tree.column("Remarks", width=150, anchor="w")
        self.tree.column("Edit", width=75, anchor="center")
        self.tree.column("Delete", width=75, anchor="center")

        scrollbar = Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        Button(
            self,
            text="Refresh",
            command=self.load_collections,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        self.tree.bind("<Button-1>", self.on_item_click)
        self.load_collections()

 
    def load_collections(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()

            collections = (
                session.query(
                    BillCollection,
                    ShopProfile.shop_name.label("shop_name"),
                    BillInfo.bill_month.label("bill_month"),
                    BillInfo.bill_year.label("bill_year"),
                    BankAccount.bank_name.label("bank_name")
                )
                .join(ShopProfile, ShopProfile.id == BillCollection.shop_id)
                .join(BillInfo, BillInfo.id == BillCollection.bill_id)
                .outerjoin(BankAccount, BankAccount.id == BillCollection.bank_id)
                .all()
            )

            for bill, shop_name,bill_month,bill_year,bank_name in collections:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        bill.id,
                        shop_name or "N/A",
                        f"{bill_month}/{bill_year}" or "N/A",
                        bill.trans_date.strftime("%Y-%m-%d") if bill.trans_date else "N/A",
                        bill.trans_mode,
                        f"{bill.trans_amount:.2f}",
                        f"{bill.pay_amount:.2f}" if bill.pay_amount else "0.00",
                        f"{bill.due_amount:.2f}" if bill.due_amount else "0.00",
                        bank_name or "N/A",
                        bill.check_no or "N/A",
                        bill.remarks or "",
                        "👁 View",
                        "Edit",
                        "Delete"
                    ),
                    tags=(bill.id,)
                )

            session.close()

        except Exception as e:
            Messagebox.show_error(f"Error loading collections: {str(e)}", "Error", parent=self)
            print(f"Error loading collections: {str(e)}")
            
    def on_item_click(self, event):
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            collection_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            # Adjusted column indices (View=11, Delete=12)
            if col_num == 12:  # Delete column
                self.delete_collection(collection_id)
            elif col_num == 11:  # View (eye) column
                self.view_bill_collection_details(collection_id)

    def edit_collection(self, collection_id):
        session = Session()
        collection = session.query(BillCollection).filter_by(id=collection_id).first()
        session.close()

        if collection:
            Messagebox.show_info(
                message=f"Editing Collection ID: {collection.id}",
                title="Edit Collection",
                parent=self
            )
            # Implement form popup for editing if needed

    def view_bill_collection_details(self, collection_id):
        """Open detail view for selected bill Collection"""
        detail_window = Toplevel(self)
        detail_window.title(f"Bill Collection Details - #{collection_id}")
        detail_window.geometry("800x600")
        
        # print(f"Bill Id: {bill_id}")
        # Assuming you have a BillDetailView class
        BillCollectionShowView(detail_window, collection_id).pack(fill="both", expand=True)

    def view_collection_details(self, collection_id):
        try:
            session = Session()
            collection = session.query(
                BillCollection,
                ShopProfile.shop_name.label("shop_name"),
                BillInfo.bill_month.label("bill_month"),
                BillInfo.bill_year.label("bill_year"),
                BankAccount.bank_name.label("bank_name")
            ).join(
                ShopProfile, ShopProfile.id == BillCollection.shop_id
            ).join(
                BillInfo, BillInfo.id == BillCollection.bill_id
            ).outerjoin(
                BankAccount, BankAccount.id == BillCollection.bank_id
            ).filter(
                BillCollection.id == collection_id
            ).first()

            if collection:
                bill, shop_name, bill_month,bill_year ,bank_name = collection

                details = [
                    f"ID: {bill.id}",
                    f"Shop: {shop_name or 'N/A'}",
                    f"Bill For: {bill_month}/{bill_year or 'N/A'}",
                    f"Date: {bill.trans_date.strftime('%Y-%m-%d') if bill.trans_date else 'N/A'}",
                    f"Mode: {bill.trans_mode}",
                    f"Amount: ₹{bill.trans_amount:.2f}",
                    f"Pay Amount: ₹{bill.pay_amount:.2f}" if bill.pay_amount else "Pay Amount: 0.00BDT",
                    f"Due Amount: ₹{bill.due_amount:.2f}" if bill.due_amount else "Due Amount: 0.00BDT",
                    f"Bank: {bank_name or 'N/A'}",
                    f"Cheque No: {bill.check_no or 'N/A'}",
                    f"Remarks: {bill.remarks or 'N/A'}"
                ]

                Messagebox.show_info(
                    title="Collection Details",
                    message="\n".join(details),
                    parent=self
                )
            else:
                Messagebox.show_warning("Collection not found", "Warning", parent=self)
                print(f"Collection not found: {collection_id}")

            session.close()

        except Exception as e:
            Messagebox.show_error(f"Error loading details: {str(e)}", "Error", parent=self)

    def delete_collection(self, collection_id):
        try:
            session = Session()
            item = session.query(BillCollection).filter_by(id=collection_id).first()

            if item:
                result = Messagebox.show_question(
                    message=f"Delete Collection ID {item.id}?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(item)
                    session.commit()
                    self.load_collections()
                    Messagebox.show_info("Deleted successfully!", "Success", parent=self)

            session.close()

        except Exception as e:
            Messagebox.show_error(f"Error deleting collection: {str(e)}", "Error", parent=self)
