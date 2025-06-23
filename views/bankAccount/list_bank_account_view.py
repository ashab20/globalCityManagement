import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from sqlalchemy.orm import sessionmaker
from models.BankAccount import BankAccount
from utils.database import Session
from views.bankAccount.create_bank_account_view import CreateBankAccountView

class ListBankAccountView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self, 
            columns=("Bank Name", "Account Number", "Status", "Entry By"), 
            show="headings"
        )
        
        # Define column headings
        self.tree.heading("Bank Name", text="Bank Name")
        self.tree.heading("Account Number", text="Account Number")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Entry By", text="Entry By")
        
        # Set column widths
        self.tree.column("Bank Name", width=150)
        self.tree.column("Account Number", width=150)
        self.tree.column("Status", width=100)
        self.tree.column("Entry By", width=100)
        
        # Add vertical scrollbar
        yscrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=yscrollbar.set)

        # Add horizontal scrollbar
        xscrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview,
            bootstyle="primary-round"
        )
        self.tree.configure(xscrollcommand=xscrollbar.set)

        # Pack widgets
        self.tree.pack(side="top", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar.pack(side="bottom", fill="x")
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10)
        
        # Edit and Delete buttons
        ttk.Button(button_frame, text="Edit", command=self.edit_bank_account, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_bank_account, bootstyle="danger").pack(side="left", padx=5)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_bank_account)
        
        # Load initial data
        self.load_bank_accounts()
    
    def load_bank_accounts(self):
        """Load bank accounts from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        session = Session()
        try:
            bank_accounts = session.query(BankAccount).all()
            
            for bank_account in bank_accounts:
                # Convert status to readable text
                status_text = "Active" if str(bank_account.status) == "1" else "Deactive"
                
                # Insert into treeview
                item = self.tree.insert("", "end", values=(
                    bank_account.bank_name,
                    bank_account.account_no,
                    status_text,
                    bank_account.entry_by
                ), tags=(bank_account.id,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load bank accounts: {str(e)}")
        finally:
            session.close()
    
    def edit_bank_account(self, event=None):
        """Open edit window for selected bank account."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a bank account to edit.")
            return
        
        # Get the bank account ID from the item's tag
        bank_account_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            bank_account = session.query(BankAccount).filter_by(id=bank_account_id).first()
            
            if bank_account:
                # Create a new window for editing
                edit_window = ttk.Toplevel(title="Edit Bank Account")
                edit_window.geometry("500x400")
                
                # Create edit view
                edit_view = CreateBankAccountView(edit_window, existing_bank_account=bank_account)
                edit_view.pack(fill="both", expand=True)
                
                # Add a callback to refresh list after editing
                def on_save():
                    self.load_bank_accounts()
                    edit_window.destroy()
                
                edit_view.save_button.config(command=on_save)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load bank account for editing: {str(e)}")
        finally:
            session.close()
    
    def delete_bank_account(self):
        """Delete the selected bank account."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a bank account to delete.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this bank account?")
        if not confirm:
            return
        
        # Get the bank account ID from the item's tag
        bank_account_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            bank_account = session.query(BankAccount).filter_by(id=bank_account_id).first()
            
            if bank_account:
                session.delete(bank_account)
                session.commit()
                
                # Refresh the list
                self.load_bank_accounts()
                messagebox.showinfo("Success", "Bank account deleted successfully.")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Could not delete bank account: {str(e)}")
        finally:
            session.close()
