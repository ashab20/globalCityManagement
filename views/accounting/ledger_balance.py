import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils.database import Session
from ttkbootstrap.dialogs import Messagebox
from models.acc_head_of_accounts import AccHeadOfAccounts
from datetime import datetime
from controllers.accounting_controller import AccountingController
from tkinter import StringVar
class LedgerBalanceView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.head_id = StringVar()
        self.from_date = StringVar()
        self.to_date = StringVar()
        self.head_mapping = {}  # Dictionary to map head names to their IDs
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))  # Better size for button

        # Main container (acts as parent layout holder)
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True, anchor="n")  # Fill all but anchor top

        # Create form inside main_container
        self.create_form()

    def create_form(self):
        """Creates the ledger balance form."""
        form_frame = ttk.Frame(self.main_container)  # Use main_container here
        form_frame.pack(fill="x", pady=(10, 0), anchor="n")

        # Page title
        title_label = ttk.Label(
            form_frame,
            text="Ledger Balance",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 10), anchor="center")

        # Input row
        input_row = ttk.Frame(form_frame)
        input_row.pack(fill="x", padx=10)

        label_style = {"bootstyle": "primary", "font": ("Helvetica", 10)}
        entry_style = {"font": ("Helvetica", 10)}

        # Head of Account
        ttk.Label(input_row, text="Head of Account:", **label_style).grid(row=0, column=0, padx=5, pady=(0, 2), sticky="w")
        self.head_of_account_combobox = ttk.Combobox(
            input_row,
            state="readonly", 
            width=24, 
            **entry_style,
            textvariable=self.head_id
        )

        self.head_of_account_combobox.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

        # From Date
        ttk.Label(input_row, text="From Date:", **label_style).grid(row=0, column=1, padx=5, pady=(0, 2), sticky="w")
        self.from_date_picker = ttk.DateEntry(
            input_row, 
            dateformat="%Y-%m-%d", 
            firstweekday=6, 
            bootstyle="primary", 
            width=20,
            startdate=None  # Start with empty date
        )
        self.from_date_picker.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

        # To Date
        ttk.Label(input_row, text="To Date:", **label_style).grid(row=0, column=2, padx=5, pady=(0, 2), sticky="w")
        self.to_date_picker = ttk.DateEntry(
            input_row, 
            dateformat="%Y-%m-%d", 
            firstweekday=6, 
            bootstyle="primary", 
            width=20,
            startdate=None  # Start with empty date
        )
        self.to_date_picker.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")

        # Search button
        self.search_button = ttk.Button(
            form_frame,
            text="Search",
            command=self.search_ledger,
            bootstyle="primary-outline",
            width=20
        )
        self.search_button.pack(pady=(0, 10), anchor="center")

        # Table frame inside main_container (not self)
        self.table_frame = ttk.Frame(self.main_container)
        self.table_frame.pack(fill="both", expand=True)

        self.load_head_of_accounts()

    def load_head_of_accounts(self):
        """Loads head of accounts into the combobox."""
        try:
            session = Session()
            head_of_accounts = AccHeadOfAccounts.get_head_of_accounts(session)
            
            # Create a dictionary to map display names to IDs
            self.head_mapping = {f"{head.head_name} (REF: {head.id})": head.id for head in head_of_accounts}
            
            # Set the display values (head names) in the combobox
            self.head_of_account_combobox['values'] = list(self.head_mapping.keys())
            
            session.close()
        except Exception as e:
            Messagebox.show_error(message=f"Error loading head of accounts: {str(e)}", title="Error", parent=self)

    def search_ledger(self):
        """Handle ledger search and display results."""
        selected_head_display = self.head_of_account_combobox.get()
        from_date = self.from_date_picker.entry.get()
        to_date = self.to_date_picker.entry.get()

        # Get the actual head ID from the mapping
        selected_head_id = self.head_mapping.get(selected_head_display) if selected_head_display else None

        # print("selected_head_display", selected_head_display)
        # print("selected_head_id", selected_head_id)
        # print("from_date", from_date)
        # print("to_date", to_date)

        if not all([selected_head_display, from_date, to_date]):
            Messagebox.show_error(message="All fields are required!", title="Validation Error", parent=self)
            return

        try:
            # Get ledger balance using the head ID
            session = Session()
            ledger_balance, prev_amount, prev_drcr_type = AccountingController.get_ledger_balance(session, head_id=selected_head_id, frm_dt=from_date, to_dt=to_date)
            session.close()
            # Clear previous table
            for widget in self.table_frame.winfo_children():
                widget.destroy()

            # Set up Treeview
            columns = ("Date", "Particulars", "Reference", "Debit", "Credit", "Balance")
            tree = ttk.Treeview(
                self.table_frame, columns=columns, show="headings", height=10, bootstyle="primary"
            )
            tree.pack(fill="both", expand=True, padx=10, pady=10)

            for col in columns:
                tree.heading(col, text=col.capitalize())
                tree.column(col, anchor="center")

            # Populate rows
            for row in ledger_balance:
                balance = 0
                date = row[0]
                particulars = row[1]
                reference = row[2]
                amount = float(row[3])
                drcr_type = row[4]

                # need to show prevous amount and crdr type
                if prev_drcr_type == 'dr':
                    balance =  float(prev_amount) + amount
                else:
                    balance =  float(prev_amount) - amount

                # need to show prevous amount and crdr type
                tree.insert("", "end", values=(date, particulars, reference, amount, drcr_type, balance))
                
        except Exception as e:
            Messagebox.show_error(message=f"Error searching ledger: {str(e)}", title="Error", parent=self)
