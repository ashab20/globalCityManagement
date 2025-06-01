import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.BankAccount import BankAccount
from utils.database import Session


class ListOfBankAccountView(ttk.Frame):
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

        # Create bank account list
        self.create_bank_account_list()

    def create_bank_account_list(self):
        """Creates the bank account list view."""
        # Define correct columns
        columns = ("ID", "Bank Name", "Account Number", "Status", "Entry By", "Entry Time", "Edit", "Delete")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure correct column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Bank Name", text="Bank Name")
        self.tree.heading("Account Number", text="Account Number")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Entry By", text="Entry By")
        self.tree.heading("Entry Time", text="Entry Time")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Bank Name", width=150, anchor="w")
        self.tree.column("Account Number", width=150, anchor="w")
        self.tree.column("Status", width=80, anchor="center")
        self.tree.column("Entry By", width=120, anchor="w")
        self.tree.column("Entry Time", width=150, anchor="w")
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

        # Load bank accounts
        self.load_bank_accounts()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_bank_accounts,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)

    def load_bank_accounts(self):
        """Load bank accounts from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            accounts = session.query(BankAccount).all()

            for account in accounts:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        account.id,
                        account.bank_name,
                        account.account_no,
                        "Active" if account.status == 1 else "Inactive",
                        account.entry_by,
                        account.entry_time.strftime("%Y-%m-%d %H:%M") if account.entry_time else "N/A",
                        "Edit",
                        "Delete"
                    ),
                    tags=(account.id,)  # Store account ID in tag
                )

            session.close()

        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading bank accounts: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            # Get the account ID from the row's tag
            account_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 8:  # Delete column
                self.delete_bank_account_by_id(account_id)
            elif col_num == 7:  # Edit column
                self.edit_bank_account(account_id)

    def edit_bank_account(self, account_id):
        """Edit bank account details."""
        session = Session()
        account = session.query(BankAccount).filter_by(id=account_id).first()
        session.close()

        if account:
            Messagebox.show_info(
                message=f"Editing Bank Account ID: {account.id}",
                title="Edit Bank Account",
                parent=self
            )
            # Implement edit functionality here (open form, update fields, save changes)

    def delete_bank_account_by_id(self, account_id):
        """Delete bank account by ID with confirmation."""
        try:
            session = Session()
            account_to_delete = session.query(BankAccount).filter_by(id=account_id).first()

            if account_to_delete:
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete bank account '{account_to_delete.bank_name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(account_to_delete)
                    session.commit()

                    # Refresh bank account list
                    self.load_bank_accounts()

                    Messagebox.show_info(
                        message="Bank account deleted successfully!",
                        title="Success",
                        parent=self
                    )

            session.close()

        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting bank account: {str(e)}",
                title="Error",
                parent=self
            )
