import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from sqlalchemy.orm import sessionmaker
from models.JournalVoucher import JournalVoucher
from utils.database import Session
from datetime import datetime

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
        self.bank_acc_id = StringVar()
        self.cheque_no = StringVar()

        # UI Components
        self.create_form()

        # If editing an existing voucher, pre-fill the form
        if existing_voucher:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing journal voucher details."""
        self.head_id.set(str(self.existing_voucher.head_id))
        self.trans_type.set(self.existing_voucher.trans_type)
        self.trans_mode.set(self.existing_voucher.trans_mode)
        self.trans_date.set(self.existing_voucher.trans_date)
        self.trans_amount.set(str(self.existing_voucher.trans_amount))
        self.remarks.set(self.existing_voucher.remarks)
        self.entry_by.set(self.existing_voucher.entry_by)
        self.bank_acc_id.set(self.existing_voucher.bank_acc_id)
        self.cheque_no.set(self.existing_voucher.cheque_no)

    def create_form(self):
        """Creates the form for entering journal voucher details."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        fields = [
            ("Head ID:", self.head_id),
            ("Transaction Type:", self.trans_type),
            ("Transaction Mode:", self.trans_mode),
            ("Transaction Date:", self.trans_date),
            ("Transaction Amount:", self.trans_amount),
            ("Remarks:", self.remarks),
            ("Entry By:", self.entry_by),
            ("Bank Account ID:", self.bank_acc_id),
            ("Cheque No:", self.cheque_no)
        ]

        for idx, (label, var) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(form_frame, textvariable=var, width=40).grid(row=idx, column=1, padx=5, pady=5)

        # Submit Button
        submit_text = "Save Journal Voucher" if not self.existing_voucher else "Update Journal Voucher"
        submit_command = self.save_journal_voucher
        self.save_button = ttk.Button(
            self, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="success"
        )
        self.save_button.pack(pady=(10, 0))

    def save_journal_voucher(self):
        """Saves or updates the journal voucher in the database."""
        try:
            session = Session()
            
            if self.existing_voucher:
                # Update existing journal voucher
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
                voucher.bank_acc_id = self.bank_acc_id.get()
                voucher.cheque_no = self.cheque_no.get()
                
                message = "Journal Voucher updated successfully!"
            else:
                # Create new journal voucher
                new_voucher = JournalVoucher(
                    head_id=int(self.head_id.get()),
                    trans_type=self.trans_type.get(),
                    trans_mode=self.trans_mode.get(),
                    trans_date=self.trans_date.get(),
                    trans_amount=float(self.trans_amount.get()),
                    remarks=self.remarks.get(),
                    entry_by=self.entry_by.get(),
                    entry_time=datetime.now(),
                    bank_acc_id=self.bank_acc_id.get(),
                    cheque_no=self.cheque_no.get()
                )
                session.add(new_voucher)
                message = "Journal Voucher added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving journal voucher: {str(e)}", title="Error", parent=self)
            print(f"Error saving journal voucher: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.head_id.set("")
        self.trans_type.set("")
        self.trans_mode.set("")
        self.trans_date.set("")
        self.trans_amount.set("")
        self.remarks.set("")
        self.entry_by.set("")
        self.bank_acc_id.set("")
        self.cheque_no.set("")
