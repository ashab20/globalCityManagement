import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from sqlalchemy.orm import sessionmaker
from models.JournalVoucher import JournalVoucher
from utils.database import Session
from views.journalVoucher.create_journal_voucher import CreateJournalVoucherView

class ListJournalVoucherView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self, 
            columns=("Date", "Voucher Type", "Description", "Amount"), 
            show="headings"
        )
        
        # Define column headings
        self.tree.heading("Date", text="Date")
        self.tree.heading("Voucher Type", text="Voucher Type")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        
        # Set column widths
        self.tree.column("Date", width=100)
        self.tree.column("Voucher Type", width=150)
        self.tree.column("Description", width=200)
        self.tree.column("Amount", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, bootstyle="primary-round", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10)
        
        # Edit and Delete buttons
        ttk.Button(button_frame, text="Edit", command=self.edit_journal_voucher, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_journal_voucher, bootstyle="danger").pack(side="left", padx=5)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_journal_voucher)
        
        # Load initial data
        self.load_journal_vouchers()
    
    def load_journal_vouchers(self):
        """Load journal vouchers from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        session = Session()
        try:
            journal_vouchers = session.query(JournalVoucher).all()
            
            for voucher in journal_vouchers:
                # Insert into treeview
                item = self.tree.insert("", "end", values=(
                    voucher.trans_date,
                    voucher.trans_type,
                    voucher.remarks,
                    voucher.trans_amount
                ), tags=(voucher.id,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load journal vouchers: {str(e)}")
        finally:
            session.close()
    
    def edit_journal_voucher(self, event=None):
        """Open edit window for selected journal voucher."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a journal voucher to edit.")
            return
        
        # Get the journal voucher ID from the item's tag
        voucher_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            voucher = session.query(JournalVoucher).filter_by(id=voucher_id).first()
            
            if voucher:
                # Create a new window for editing
                edit_window = ttk.Toplevel(title="Edit Journal Voucher")
                edit_window.geometry("500x400")
                
                # Create edit view
                edit_view = CreateJournalVoucherView(edit_window, existing_voucher=voucher)
                edit_view.pack(fill="both", expand=True)
                
                # Add a callback to refresh list after editing
                def on_save():
                    self.load_journal_vouchers()
                    edit_window.destroy()
                
                edit_view.save_button.config(command=on_save)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load journal voucher for editing: {str(e)}")
        finally:
            session.close()
    
    def delete_journal_voucher(self):
        """Delete the selected journal voucher."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a journal voucher to delete.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this journal voucher?")
        if not confirm:
            return
        
        # Get the journal voucher ID from the item's tag
        voucher_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            voucher = session.query(JournalVoucher).filter_by(id=voucher_id).first()
            
            if voucher:
                session.delete(voucher)
                session.commit()
                
                # Refresh the list
                self.load_journal_vouchers()
                messagebox.showinfo("Success", "Journal voucher deleted successfully.")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Could not delete journal voucher: {str(e)}")
        finally:
            session.close()
