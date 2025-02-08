import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.JournalVoucher import JournalVoucher
from utils.database import Session


class ListOfJournalVoucherView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent

        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Create journal voucher list
        self.create_journal_voucher_list()

    def create_journal_voucher_list(self):
        """Creates the journal voucher list view."""
        columns = ("ID", "Head ID", "Transaction Type", "Mode", "Date", "Amount", "Bank Account", "Cheque No", "Entry By", "Entry Time", "Edit", "Delete")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure column headings
        for col in columns:
            self.tree.heading(col, text=col)

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Head ID", width=80, anchor="center")
        self.tree.column("Transaction Type", width=120, anchor="w")
        self.tree.column("Mode", width=100, anchor="w")
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Bank Account", width=120, anchor="center")
        self.tree.column("Cheque No", width=100, anchor="center")
        self.tree.column("Entry By", width=100, anchor="center")
        self.tree.column("Entry Time", width=150, anchor="center")
        self.tree.column("Edit", width=75, anchor="center")
        self.tree.column("Delete", width=75, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load journal vouchers
        self.load_journal_vouchers()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_journal_vouchers,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)

    def load_journal_vouchers(self):
        """Load journal vouchers from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            vouchers = session.query(JournalVoucher).all()

            for voucher in vouchers:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        voucher.id,
                        voucher.head_id,
                        voucher.trans_type,
                        voucher.trans_mode if voucher.trans_mode else "N/A",
                        voucher.trans_date,
                        f"{voucher.trans_amount:.2f}",
                        voucher.bank_acc_id,
                        voucher.cheque_no if voucher.cheque_no else "N/A",
                        voucher.entry_by,
                        voucher.entry_time.strftime("%Y-%m-%d %H:%M") if voucher.entry_time else "N/A",
                        "Edit",
                        "Delete"
                    ),
                    tags=(voucher.id,)  # Store voucher ID in tag
                )

            session.close()

        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading journal vouchers: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            voucher_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 11:  # Delete column
                self.delete_journal_voucher(voucher_id)
            elif col_num == 10:  # Edit column
                self.edit_journal_voucher(voucher_id)

    def edit_journal_voucher(self, voucher_id):
        """Edit journal voucher details."""
        session = Session()
        voucher = session.query(JournalVoucher).filter_by(id=voucher_id).first()
        session.close()

        if voucher:
            Messagebox.show_info(
                message=f"Editing Journal Voucher ID: {voucher.id}",
                title="Edit Journal Voucher",
                parent=self
            )
            # Implement edit functionality here (open form, update fields, save changes)

    def delete_journal_voucher(self, voucher_id):
        """Delete journal voucher by ID with confirmation."""
        try:
            session = Session()
            voucher_to_delete = session.query(JournalVoucher).filter_by(id=voucher_id).first()

            if voucher_to_delete:
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete Journal Voucher ID {voucher_to_delete.id}?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(voucher_to_delete)
                    session.commit()

                    # Refresh voucher list
                    self.load_journal_vouchers()

                    Messagebox.show_info(
                        message="Journal voucher deleted successfully!",
                        title="Success",
                        parent=self
                    )

            session.close()

        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting journal voucher: {str(e)}",
                title="Error",
                parent=self
            )
