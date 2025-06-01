import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import IntVar, StringVar, messagebox, Canvas, Frame, Scrollbar
from sqlalchemy.orm import sessionmaker
from models.JournalVoucher import JournalVoucher
from utils.database import Session
from datetime import datetime
from models.acc_head_of_accounts import AccHeadOfAccounts
from models.BankAccount import BankAccount
from utils.database import Session
from controllers.accounting_controller import AccountingController


class CreateJournalVoucherView(ttk.Frame):
    def __init__(self, parent, existing_voucher=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_voucher = existing_voucher

        # StringVars for input fields
        self.head_id = StringVar()
        self.trans_type = StringVar()
        self.trans_mode = StringVar()
        self.trans_date = StringVar()
        self.trans_amount = StringVar()
        self.remarks = StringVar()
        self.entry_by = StringVar()
        self.bank_name = StringVar()
        self.selected_bank_id = None
        self.cheque_no = StringVar()
        
        # Store data
        self.heads_dict = {}
        self.bank_dict = {}
        
        # Load heads
        self.load_heads()
        self.load_banks()

        # UI Components
        self.create_scrollable_form()

        # If editing an existing voucher, pre-fill the form
        if existing_voucher:
            self.pre_fill_form()

    def load_heads(self):
        """Load heads from acc_head_of_accounts table"""
        try:
            session = Session()
            heads = session.query(AccHeadOfAccounts).filter_by(isActive=1).all()
            
            # Create a dictionary of head names and IDs
            self.heads_dict = {head.head_name: head.id for head in heads}
            
            session.close()
        except Exception as e:
            print(f"Error loading heads: {str(e)}")
            self.heads_dict = {}
            
    def load_banks(self):
        """Load heads from acc_head_of_accounts table"""
        try:
            session = Session()
            banks = BankAccount.get_banks()
            print(f"Banks: {banks}")
            # Create a dictionary of head names and IDs
            self.bank_dict = {bank.bank_name: bank.id for bank in banks}
            
            session.close()
        except Exception as e:
            print(f"Error loading heads: {str(e)}")
            self.bank_dict = {}

    def create_scrollable_form(self):
        """Creates a scrollable form layout."""
        # Canvas and Scrollbar
        canvas = Canvas(self)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_form(scrollable_frame)

    def create_form(self, parent):
        """Creates the form for entering journal voucher details inside a scrollable frame."""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill="x", pady=10)

        # Create two columns container
        columns_frame = ttk.Frame(form_frame)
        columns_frame.pack(fill="x", expand=True)

        # Create two columns
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # Store selected head name for display
        self.selected_head_name = StringVar()
        self.selected_bank_name = StringVar()

        # Transaction Type (Combobox)
        ttk.Label(left_frame, text="Transaction Type:").pack(anchor="w")
        self.trans_type_combobox = ttk.Combobox(
            left_frame,
            textvariable=self.trans_type,
            values=["Recipt", "Payment", "Journal Voucher", "Withdraw From Bank", "Deposite To Bank"],
            state="readonly",
            width=30
        )
        self.trans_type_combobox.pack(fill="x", pady=(0, 10))

        # Bind to update head list when changed
        self.trans_type_combobox.bind("<<ComboboxSelected>>", self.on_trans_type_change)

        # Head selection
        ttk.Label(left_frame, text="Head:").pack(anchor="w")
        self.head_combobox = ttk.Combobox(
            left_frame,
            textvariable=self.selected_head_name,
            values=list(self.heads_dict.keys()),
            state="readonly",
            width=30
        )
        self.head_combobox.pack(fill="x", pady=(0, 10))

        
        
        # Bind selection event
        def on_head_select(event):
            selected_head_name = self.head_combobox.get()
            if selected_head_name in self.heads_dict:
                self.head_id.set(str(self.heads_dict[selected_head_name]))
        
        self.head_combobox.bind('<<ComboboxSelected>>', on_head_select)

        

        # Transaction Mode
        # ttk.Label(left_frame, text="Transaction Mode:").pack(anchor="w")
        # ttk.Entry(left_frame, textvariable=self.trans_mode).pack(fill="x", pady=(0, 10))
        ttk.Label(left_frame, text="Transaction Mode:").pack(anchor="w")
        self.trans_type_combobox = ttk.Combobox(
            left_frame,
            textvariable=self.trans_mode,
            values=["Cash", "Cheque"],
            state="readonly",
            width=30
        )
        self.trans_type_combobox.pack(fill="x", pady=(0, 10))

        # Transaction Date
        ttk.Label(left_frame, text="Transaction Date:").pack(anchor="w")
        self.date_picker = ttk.DateEntry(
            left_frame,
            dateformat="%Y-%m-%d",  # Format: YYYY-MM-DD
            firstweekday=6,  # 6 for Sunday
            bootstyle="primary"
        )
        self.date_picker.pack(fill="x", pady=(0, 10))
        
        # Bind date selection to update trans_date StringVar
        def on_date_select():
            self.trans_date.set(self.date_picker.entry.get())
        
        self.date_picker.entry.configure(textvariable=self.trans_date)

        # Right column
        
         # Bank Account ID
        ttk.Label(right_frame, text="Bank:").pack(anchor="w")
        self.bank_combobox= ttk.Combobox(
            right_frame,
            textvariable=self.bank_name,
            values=list(self.bank_dict.keys()),
            state="readonly",
            width=30
        )
        self.bank_combobox.pack(fill="x", pady=(0, 10))
        self.bank_combobox.bind("<<ComboboxSelected>>", self.on_bank_selected)
        
        
        # Transaction Amount
        ttk.Label(right_frame, text="Transaction Amount:").pack(anchor="w")
        ttk.Entry(right_frame, textvariable=self.trans_amount).pack(fill="x", pady=(0, 10))

       
        
        # ttk.Label(right_frame, text="Bank Name:").pack(anchor="w")
        # ttk.Entry(right_frame, textvariable=self.bank_name).pack(fill="x", pady=(0, 10))

        # Cheque No
        ttk.Label(right_frame, text="Cheque No:").pack(anchor="w")
        ttk.Entry(right_frame, textvariable=self.cheque_no).pack(fill="x", pady=(0, 10))

         # Remarks
        ttk.Label(right_frame, text="Remarks:").pack(anchor="w")
        ttk.Entry(right_frame, textvariable=self.remarks).pack(fill="x", pady=(0, 10))

        # Submit Button - Centered at the bottom of form_frame
        submit_text = "Save Journal Voucher" if not self.existing_voucher else "Update Journal Voucher"
        submit_command = self.save_journal_voucher
        self.save_button = ttk.Button(
            form_frame,
            text=submit_text,
            command=submit_command,
            bootstyle="primary",
            width=20
        )
        self.save_button.pack(pady=(20, 0))
    
    def on_trans_type_change(self):
        trans_type = self.trans_type.get()
        self.load_heads(trans_type)  # Reload based on type
        self.head_combobox['values'] = list(self.heads_dict.keys())  # Update head list in UI


    def pre_fill_form(self):
        """Pre-fill form with existing journal voucher details."""
        # Find head name from ID
        head_name = next((name for name, id in self.heads_dict.items() 
                         if str(id) == str(self.existing_voucher.head_id)), "")
        self.selected_head_name.set(head_name)
        self.head_id.set(str(self.existing_voucher.head_id))
        
        self.trans_type.set(self.existing_voucher.trans_type)
        self.trans_mode.set(self.existing_voucher.trans_mode)
        
        # Set date in date picker if it exists
        if self.existing_voucher.trans_date:
            self.date_picker.entry.delete(0, "end")
            self.date_picker.entry.insert(0, self.existing_voucher.trans_date)
            self.trans_date.set(self.existing_voucher.trans_date)
        
        self.trans_amount.set(str(self.existing_voucher.trans_amount))
        self.remarks.set(self.existing_voucher.remarks)
        self.entry_by.set(self.existing_voucher.entry_by)
        self.bank_name.set(self.existing_voucher.bank_name)
        self.cheque_no.set(self.existing_voucher.cheque_no)

    def save_journal_voucher(self):
        """Saves or updates the journal voucher in the database."""
        try:
            session = Session()

            print(f"Bank Dictionalry:{self.bank_dict}")
            
            if self.existing_voucher:
                voucher = session.query(JournalVoucher).filter_by(id=self.existing_voucher.id).first()
                if not voucher:
                    raise ValueError("Journal Voucher not found")
                
                voucher.head_id = int(self.head_id.get())
                voucher.trans_type = self.trans_type.get()
                voucher.trans_mode = self.trans_mode.get()
                voucher.trans_date = self.trans_date.get()
                voucher.trans_amount = float(self.trans_amount.get())
                voucher.remarks = self.remarks.get()
                voucher.entry_by = self.entry_by.get()
                voucher.entry_time = datetime.now()
                voucher.bank_name = self.bank_name.get()
                voucher.cheque_no = self.cheque_no.get()
                
                message = "Journal Voucher updated successfully!"
            else:
                #INSERT
                # Data Filtering according to transaction type
                if self.trans_type.get() == "payment":

                    headBalance = 0
                    # check transaction mode
                    if self.trans_mode.get() == "cash":
                        # get head balance cash IN Head From Ledger Current
                        self.headBalance = AccountingController.get_head_balance(session, 4)
                        print("cash")
                    else:
                        # get bank head
                        headId = AccountingController.get_bank_head_id(session, self.bank_name.get())
                        self.headBalance = AccountingController.get_head_balance(session, headId)
                        print("cheque")

                    if self.trans_type.get() == "payment" or self.trans_type.get() == "deposite to bank" and self.trans_amount.get() > self.headBalance:
                        ttk.dialogs.Messagebox.show_error(message="Insufficient balance", title="Error", parent=self)
                        return
                elif self.trans_type.get() == "deposite to bank":
                    # get bank head
                    headId = AccountingController.get_bank_head_id(session, self.bank_name.get())
                    self.headBalance = AccountingController.get_head_balance(session, headId)
                    print("head id",self.head_id.get())
                    print("bank name",self.bank_name.get())

                else :
                    cashSign = '+'
                    cashTrs = 'cr'
                    headTrs = 'dr'
                    head_id = self.head_id.get()
                    cheque_no = self.cheque_no.get()
                    cashBankHead = 4

                    if self.trans_mode.get() == "receipt":
                        cashTrs = 'cr'
                        headTrs = 'dr'
                        if self.trans_mode.get() == "cash":
                            cashBankHead = 4
                        else:
                            # get bank head
                            headId = AccountingController.get_bank_head_id(session, self.selected_bank_id)
                            cashBankHead = headId
                        cashSign = '+'
                    elif self.trans_mode.get() == "payment":
                        cashTrs = 'cr'
                        headTrs = 'dr'
                        if self.trans_mode.get() == "cash":
                            cashBankHead = 4
                        else:
                            # get bank head
                            headId = AccountingController.get_bank_head_id(session, self.selected_bank_id)
                            cashBankHead = headId
                        cashSign = '-'
                    elif self.trans_mode.get() == "withdraw from bank":
                        cashTrs = 'dr'
                        headTrs = 'cr'
                        cashBankHead = 4
                        head_id = self.head_id.get()
                        cheque_no = self.cheque_no.get()
                        cashSign = '+'
                    elif self.trans_mode.get() == "deposite to bank":
                        cashTrs = 'cr'
                        headTrs = 'dr'
                        cashBankHead = 4
                        head_id = self.head_id.get()
                        cheque_no = self.cheque_no.get()
                        cashSign = '-'
                    print("Head",int(self.head_id.get()))
                    new_voucher = JournalVoucher(
                        head_id=int(self.head_id.get()),
                        trans_type=self.trans_type.get(),
                        trans_mode=self.trans_mode.get(),
                        trans_date=self.trans_date.get(),
                        trans_amount=float(self.trans_amount.get()),
                        remarks=self.remarks.get(),
                        entry_by=self.entry_by.get(),
                        entry_time=datetime.now(),
                        bank_name=self.bank_name.get(),
                        cheque_no=self.cheque_no.get()
                    )
                    session.add(new_voucher)
                    session.commit()  # Commit to get the ID
                    
                    if not head_id or not str(head_id).isdigit():
                        print("Missing or invalid head_id for second leg")
                        return

                    head_id = int(head_id)

                    # get transaction ref number
                    refNumber = AccountingController.getTransRefNumber(session)
                    # print("refNumber",refNumber,cashBankHead,new_voucher.id)
                    # Cash In Hand Transaction
                    transaction_info = [
                        cashSign, # operation_type
                        "insert",        # action_type
                        cashBankHead,   # head_id
                        new_voucher.id,            # trans_ref_id (e.g., invoice or payment ID)
                        self.trans_date.get(),    # trans_date
                        float(self.trans_amount.get()),         # amount
                        self.selected_bank_id,               #  bank_account_id
                        '1',         # user
                        None,            # prev_jour_id (not used in insert)
                        "jrnlVocr_ref_id",        # col_name in AccountJournal to store ref_id
                        refNumber,        # ref_number
                        cashTrs,            # drcr_type
                        self.remarks.get() # remarks
                    ]
                    # print("Cash transaction",transaction_info)
                    # Use the controller
                    AccountingController.manage_transaction(session, transaction_info)
                    message = "Journal Voucher added successfully!"


                    # Head transaction
                    transaction_info = [
                        cashSign, # operation_type
                        "insert",        # action_type
                        head_id,   # head_id
                        new_voucher.id,            # trans_ref_id (e.g., invoice or payment ID)
                        self.trans_date.get(),    # trans_date
                        float(self.trans_amount.get()),         # amount
                        self.selected_bank_id,               #  bank_account_id
                        self.entry_by.get(),         # user
                        None,            # prev_jour_id (not used in insert)
                        "jrnlVocr_ref_id",        # col_name in AccountJournal to store ref_id
                        refNumber,        # ref_number
                        headTrs,            # drcr_type
                        self.remarks.get() # remarks
                    ]
                    print("Head transaction",transaction_info)
                    # Use the controller
                    AccountingController.manage_transaction(session, transaction_info)
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving journal voucher: {str(e)}", title="Error", parent=self)
            print(f"Error saving journal voucher: {str(e)}")


    def on_bank_selected(self, event):
        selected_bank_name = self.bank_name.get()
        self.selected_bank_id = self.bank_dict.get(selected_bank_name)
        print(f"Selected Bank: {selected_bank_name}, ID: {self.selected_bank_id}")



    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.selected_head_name.set("")  # Clear the displayed head name
        self.head_id.set("")
        self.trans_type.set("")
        self.trans_mode.set("")
        self.trans_date.set("")
        self.trans_amount.set("")
        self.remarks.set("")
        self.entry_by.set("")
        self.bank_name.set("")
        self.cheque_no.set("")
