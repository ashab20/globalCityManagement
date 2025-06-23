import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from sqlalchemy.orm import sessionmaker
from models.BankAccount import BankAccount
from utils.database import Session
from datetime import datetime
from models.acc_head_of_accounts import AccHeadOfAccounts

class CreateBankAccountView(ttk.Frame):
    def __init__(self, parent, existing_bank_account=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_bank_account = existing_bank_account

        # StringVars for input fields
        self.bank_name = StringVar()
        self.account_no = StringVar()
        self.status = StringVar(value="Deactive")
        self.entry_by = StringVar()

        # Status mapping
        self.status_options = {"Active": "1", "Deactive": "0"}

        # UI Components
        self.create_form()

        # If editing an existing bank account, pre-fill the form
        if existing_bank_account:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing bank account details."""
        self.bank_name.set(self.existing_bank_account.bank_name)
        self.account_no.set(self.existing_bank_account.account_no)

        # Map database value back to user-friendly text
        status_text = "Active" if str(self.existing_bank_account.status) == "1" else "Deactive"
        self.status.set(status_text)

        self.entry_by.set(self.existing_bank_account.entry_by)

    def create_form(self):
        """Creates the form for entering bank account details."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        # Bank Name
        ttk.Label(form_frame, text="Bank Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.bank_name, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Account Number
        ttk.Label(form_frame, text="Account Number:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.account_no, width=40).grid(row=1, column=1, padx=5, pady=5)

        # Status
        ttk.Label(form_frame, text="Status:").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Create a combobox with user-friendly labels
        self.status_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.status, 
            values=list(self.status_options.keys()),  # Show "Active" and "Deactive"
            state="readonly", 
            width=38
        )
        self.status_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.status_combobox.set("Deactive")  # Default to "Deactive"

        # Entry By
        ttk.Label(form_frame, text="Entry By:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.entry_by, width=40).grid(row=3, column=1, padx=5, pady=5)

        # Submit Button
        submit_text = "Save Bank Account" if not self.existing_bank_account else "Update Bank Account"
        submit_command = self.save_bank_account
        self.save_button = ttk.Button(
            self, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="success"
        )
        self.save_button.pack(pady=(10, 0))

    def get_selected_status(self):
        """Returns the corresponding database value for the selected status."""
        return self.status_options[self.status.get()]  # "1" for "Active", "0" for "Deactive"

    def save_bank_account(self):
        """Saves or updates the bank account in the database."""
        try:
            session = Session()
           
            if self.existing_bank_account:
                # Update existing bank account
                bank_account = session.query(BankAccount).filter_by(id=self.existing_bank_account.id).first()
                if not bank_account:
                    raise ValueError("Bank account not found")
                
                bank_account.bank_name = self.bank_name.get()
                bank_account.account_no = self.account_no.get()
                bank_account.status = self.get_selected_status()
                bank_account.entry_by = self.entry_by.get()
                bank_account.entry_time = datetime.now()
                
                message = "Bank account updated successfully!"
            else:
                # Create new bank account
                new_account = BankAccount(
                    bank_name=self.bank_name.get(),
                    account_no=self.account_no.get(),
                    status=int(self.get_selected_status()),
                    entry_by=1,
                    entry_time=datetime.now()
                )
                session.add(new_account)
                # Flush the session to get the ID
                session.flush()
                
                print(f"New bank account ID: {new_account.id}")
                
                # Add Account Head
                account_head = AccHeadOfAccounts(
                    head_lvl4th_id=7,
                    head_name=self.bank_name.get()+" (  "+self.account_no.get()+" )",
                    remarks="",
                    bank_id=new_account.id,
                    isActive=int(self.get_selected_status()),
                    entry_by=1,
                    entry_time=datetime.now()
                )
                session.add(account_head)
                message = "Bank account added successfully!"
            
            # Commit all changes
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            session.rollback()
            session.close()
            ttk.dialogs.Messagebox.show_error(message=f"Error saving bank account: {str(e)}", title="Error", parent=self)
            print(f"Error saving bank account: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.bank_name.set("")
        self.account_no.set("")
        self.status.set("Deactive")  # Reset to "Deactive"
        self.entry_by.set("")
