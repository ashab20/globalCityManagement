import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from sqlalchemy.orm import sessionmaker
from models.JournalVoucher import JournalVoucher
from utils.database import Session
from views.journalVoucher.create_journal_voucher import CreateJournalVoucherView
from models.acc_head_of_accounts import AccHeadOfAccounts
from ttkbootstrap.dialogs import Messagebox

class ListJournalVoucherView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Create a frame for the treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        # Create Treeview
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=("Date", "Voucher Type", "Description", "Amount", "Bank Name", "Cheque No", "Entry By", "Entry Time", "Edit", "Delete"), 
            show="headings"
        )
        
        # Define column headings
        self.tree.heading("Date", text="Date")
        self.tree.heading("Voucher Type", text="Voucher Type")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Bank Name", text="Bank Name")
        self.tree.heading("Cheque No", text="Cheque No")
        self.tree.heading("Entry By", text="Entry By")
        self.tree.heading("Entry Time", text="Entry Time")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")
        
        # Set column widths
        self.tree.column("Date", width=100)
        self.tree.column("Voucher Type", width=150)
        self.tree.column("Description", width=200)
        self.tree.column("Amount", width=250)
        self.tree.column("Bank Name", width=300)
        self.tree.column("Cheque No", width=350)
        self.tree.column("Entry By", width=400)
        self.tree.column("Entry Time", width=450)
        self.tree.column("Edit", width=500)
        self.tree.column("Delete", width=100)
        
        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, bootstyle="primary-round", command=self.tree.yview)
        self.tree.configure(yscroll=v_scrollbar.set)

        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, bootstyle="primary-round", command=self.tree.xview)
        self.tree.configure(xscroll=h_scrollbar.set)

        # Layout the treeview and scrollbars
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        
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

        try:
            session = Session()
            vouchers = session.query(JournalVoucher).join(AccHeadOfAccounts, JournalVoucher.head_id == AccHeadOfAccounts.id).all()
            print(vouchers,"vouchers")
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
                        voucher.bank_name if voucher.bank_name else "N/A",
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
                Messagebox.show_info(
                    message="Journal voucher deleted successfully.",
                    title="Success",
                    parent=self
                )
            
        except Exception as e:
            session.rollback()
            Messagebox.show_error(
                message=f"Error deleting journal voucher: {str(e)}",
                title="Error",
                parent=self
            )
        finally:
            session.close()
