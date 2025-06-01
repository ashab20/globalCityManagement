from ttkbootstrap import Frame, Style, Scrollbar, Button, Treeview
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.bill_collection import BillCollection
from utils.database import Session


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
            collections = session.query(BillCollection).all()
            for col in collections:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        col.id,
                        col.shop_id,
                        col.bill_id,
                        col.trans_date.strftime("%Y-%m-%d") if col.trans_date else "N/A",
                        col.trans_mode,
                        f"{col.trans_amount:.2f}",
                        f"{col.pay_amount:.2f}" if col.pay_amount else "0.00",
                        f"{col.due_amount:.2f}" if col.due_amount else "0.00",
                        col.bank_id if col.bank_id else "N/A",
                        col.check_no if col.check_no else "N/A",
                        col.remarks or "",
                        "Edit",
                        "Delete"
                    ),
                    tags=(col.id,)
                )
            session.close()

        except Exception as e:
            Messagebox.show_error(f"Error loading collections: {str(e)}", "Error", parent=self)

    def on_item_click(self, event):
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            collection_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 13:  # Delete
                self.delete_collection(collection_id)
            elif col_num == 12:  # Edit
                self.edit_collection(collection_id)

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
