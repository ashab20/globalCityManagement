import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils.database import Session
from ttkbootstrap.dialogs import Messagebox
from models.acc_head_of_accounts import AccHeadOfAccounts
from datetime import datetime
from controllers.accounting_controller import AccountingController

class TrialBalanceView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
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
        """Creates the trial balance form."""
        form_frame = ttk.Frame(self.main_container)  # Use main_container here
        form_frame.pack(fill="x", pady=(10, 0), anchor="n")

        # Page title
        title_label = ttk.Label(
            form_frame,
            text="Trial Balance",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 10), anchor="center")

        # Input row
        input_row = ttk.Frame(form_frame)
        input_row.pack(fill="x", padx=10)

        label_style = {"bootstyle": "primary", "font": ("Helvetica", 10)}
        entry_style = {"font": ("Helvetica", 10)}

        # # Head of Account   
        # ttk.Label(input_row, text="Head of Account:", **label_style).grid(row=0, column=0, padx=5, pady=(0, 2), sticky="w")
        # self.head_of_account_combobox = ttk.Combobox(input_row, state="readonly", width=24, **entry_style)
        # self.head_of_account_combobox.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

        # From Date
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


        # # To Date
        # ttk.Label(input_row, text="To Date:", **label_style).grid(row=0, column=2, padx=5, pady=(0, 2), sticky="w")
        # self.to_date_picker = ttk.DateEntry(input_row, dateformat="%Y-%m-%d", firstweekday=6, bootstyle="primary", width=20)
        # self.to_date_picker.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")

        # Search button
        self.search_button = ttk.Button(
            form_frame,
            text="Search",
            command=self.search_trial_balance,
            bootstyle="primary-outline",
            width=20
        )
        self.search_button.pack(pady=(0, 10), anchor="center")

        # Table frame inside main_container (not self)
        self.table_frame = ttk.Frame(self.main_container)
        self.table_frame.pack(fill="both", expand=True)
        self.search_trial_balance()

    

    def search_trial_balance(self):
        """Handle ledger search and display results."""
        # selected_head = self.head_of_account_combobox.get()
        from_date = self.from_date_picker.entry.get()
        # to_date = self.to_date_picker.entry.get()
        total_debit = 0
        total_credit = 0

        if not all([from_date]):
            session = Session()
            result_rows = AccountingController.get_trial_balance(session)
            print("result_rows",result_rows)
            session.close()

             # Set up Treeview
            columns = ("sl", "particular","Ref. No", "debit", "credit")
            tree = ttk.Treeview(
                self.table_frame, columns=columns, show="headings", height=10, bootstyle="primary"
            )
            tree.pack(fill="both", expand=True, padx=10, pady=10)

            for col in columns:
                tree.heading(col, text=col.capitalize())
                tree.column(col, anchor="center")

            # print("result_rows",result_rows)
            # Populate rows
            for i, row in enumerate(result_rows, start=1):
                head_name = row[0]
                ref_id = row[1]
                amount = float(row[2])
                drcr_type = row[3]
                debit = amount if drcr_type == 'dr' else "0.00"
                credit = amount if drcr_type == 'cr' else "0.00"
                total_debit += float(debit)
                total_credit += float(credit)

                tree.insert("", "end", values=(i, head_name, ref_id, debit, credit))

        try:
            # Clear previous table
            for widget in self.table_frame.winfo_children():
                widget.destroy()

            # Format date
            tb_date = from_date

            session = Session()
            result_rows = AccountingController.get_trial_balance(session, tb_date=tb_date)
            # print("result_rows",result_rows)
            session.close()

            # Set up Treeview
            columns = ("sl", "particular", "Ref. No", "debit", "credit")
            tree = ttk.Treeview(
                self.table_frame, columns=columns, show="headings", height=10, bootstyle="primary"
            )
            tree.pack(fill="both", expand=True, padx=10, pady=10)

            for col in columns:
                tree.heading(col, text=col.capitalize())
                tree.column(col, anchor="center")

            # Populate rows
            for i, row in enumerate(result_rows, start=1):
                head_name = row[0]
                ref_id = row[1]
                drcr_type = row[3]
                amount = float(row[2])
                debit = amount if drcr_type == 'dr' else "0.00"
                credit = amount if drcr_type == 'cr' else "0.00"
                total_debit += float(debit)
                total_credit += float(credit)

                tree.insert("", "end", values=(i, head_name, ref_id, debit, credit))
        
            tree.insert("", "end", values=("", "", "Total", total_debit, total_credit))
        except Exception as e:
            Messagebox.show_error(message=f"Error searching ledger: {str(e)}", title="Error", parent=self)

