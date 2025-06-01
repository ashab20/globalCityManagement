import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.bill_info import BillInfo
from models.shop_profile import ShopProfile
from models.bill_particular import BillParticular
from utils.database import Session
import tkinter as tk
from views.billInfo.create_bill import CreateBillInfoView
from views.billInfo.bill_info import BillDetailView
from sqlalchemy.orm import joinedload

class BillInfoListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.style = ttk.Style()
        self.configure_layout()
        self.create_bill_info_list()
        self.load_bill_infos()

    def configure_layout(self):
        """Configure style and layout"""
        self.style.configure("TFrame", background="white")
        self.style.configure("TLabel", background="white")
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    def create_bill_info_list(self):
        """Create the bill list Treeview"""
        # Create Treeview with appropriate columns
        columns = (
            "ID", "Shop", "Year", "Month", 
            "Total Amount", "Previous Due", "Status", "View", "Edit", "Delete"
        )
        
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15,
            style="ActionTree.Treeview"
        )

        # Configure columns
        col_widths = [50, 150, 60, 60, 100, 100, 80, 60, 60, 60]
        col_anchors = [tk.CENTER, tk.W] + [tk.CENTER]*5 + [tk.CENTER]*3
        for col, width, anchor in zip(columns, col_widths, col_anchors):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        # Add scrollbars
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        # Grid layout (keep this for proper scrolling)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Configure style for action columns
        style = ttk.Style()
        style.configure("ActionTree.Treeview", 
                    rowheight=25,
                    font=("Helvetica", 10))
        style.map("ActionTree.Treeview",
                foreground=[("selected", "white")],
                background=[("selected", "#007bff")])

        # Bind click events
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Motion>", self.on_tree_hover)

        # Add buttons frame below the treeview
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Buttons remain the same
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_bill_infos,
            bootstyle="primary"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Add New",
            command=self.add_new_bill_info,
            bootstyle="success"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Print Bill",
            command=self.print_bill_details,
            bootstyle="info"
        ).pack(side="left", padx=5)

    def load_bill_infos(self):
        """Load bills from database"""
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        try:
            session = Session()
            bills = session.query(BillInfo).all()
            
            for bill in bills:
                shop = session.query(ShopProfile).filter_by(id=bill.shop_id).first()
                shop_name = f"{shop.shop_name} ({shop.shop_no})" if shop else "N/A"
                
                self.tree.insert("", "end", values=(
                    bill.id,
                    shop_name,
                    bill.bill_year,
                    bill.bill_month,
                    f"৳{bill.bill_amount:.2f}" if bill.bill_amount is not None else "N/A",
                    f"৳{bill.prev_due:.2f}" if bill.prev_due is not None else "N/A",
                    "Paid" if bill.status == 1 else "Pending",
                    "👁 View",
                    "✎ Edit", 
                    "🗑 Delete"
                ), tags=("clickable",))


            # Configure clickable style
            self.tree.tag_configure("clickable", foreground="#007bff")
            
            session.close()
        except Exception as e:
            Messagebox.show_error(f"Error loading bills: {str(e)}", "Database Error")

    # Add these new methods to your class
    def on_tree_hover(self, event):
        """Handle mouse hover events"""
        region = self.tree.identify("region", event.x, event.y)
        column = self.tree.identify_column(event.x)
        
        if region == "cell" and column in ["#8", "#9", "#10"]:
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")

    def on_tree_click(self, event):
        """Handle click events on the treeview"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # Convert column identifier to index (0-based)
            col_index = int(column[1:]) - 1
            
            if item and col_index >= 7:  # Action columns start at index 7
                bill_id = self.tree.item(item)['values'][0]
                
                if col_index == 7:   # View column
                    self.view_bill_details(bill_id)
                elif col_index == 8:  # Edit column
                    self.edit_bill_info(bill_id)
                elif col_index == 9:  # Delete column
                    self.delete_bill_info(bill_id)

    def view_bill_details(self, bill_id):
        """Open detail view for selected bill"""
        detail_window = ttk.Toplevel(self)
        detail_window.title(f"Bill Details - #{bill_id}")
        detail_window.geometry("800x600")
        
        # print(f"Bill Id: {bill_id}")
        # Assuming you have a BillDetailView class
        BillDetailView(detail_window, bill_id).pack(fill="both", expand=True)

    def delete_bill_info(self, bill_id):
        """Delete selected bill with confirmation"""
        if Messagebox.show_question(
            f"Are you sure you want to delete bill #{bill_id}?",
            "Confirm Deletion",
            parent=self
        ) == "Yes":
            try:
                session = Session()
                bill = session.query(BillInfo).filter_by(id=bill_id).first()
                if bill:
                    session.delete(bill)
                    session.commit()
                    self.load_bill_infos()
                session.close()
            except Exception as e:
                Messagebox.show_error(f"Error deleting bill: {str(e)}", "Deletion Error")
                
    def edit_bill_info(self, bill_id):
        """Edit selected bill"""
        try:
            session = Session()
            # Eager load relationships
            bill = session.query(BillInfo).options(
                joinedload(BillInfo.shop),
                joinedload(BillInfo.particulars)
            ).filter_by(id=bill_id).first()
            
            if bill:
                # Detach object from session
                session.expunge(bill)
                
                edit_window = ttk.Toplevel(self)
                edit_window.title(f"Edit Bill - #{bill_id}")
                edit_window.grab_set()  # Make window modal
                
                editor = CreateBillInfoView(edit_window, existing_bill_info=bill)
                editor.pack(fill="both", expand=True)
                
                editor.save_button.configure(
                    command=lambda: [
                        editor.save_bill_info(),
                        edit_window.grab_release(),
                        edit_window.destroy(),
                        self.load_bill_infos()
                    ]
                )
        except Exception as e:
            Messagebox.show_error(f"Error editing bill: {str(e)}", "Edit Error")
        finally:
            session.close()

    def open_bill_editor(self, bill):
        """Open bill editor window"""
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Edit Bill #{bill.id}")
        edit_win.geometry("800x600")

        editor = CreateBillInfoView(edit_win, existing_bill_info=bill)
        editor.pack(fill="both", expand=True)
        
        # Update save command to refresh list
        editor.save_button.configure(
            command=lambda: [
                editor.save_bill_info(),
                edit_win.destroy(),
                self.load_bill_infos()
            ]
        )

    def add_new_bill_info(self):
        """Open new bill creation window"""
        new_win = tk.Toplevel(self)
        new_win.title("Create New Bill")
        new_win.geometry("800x600")

        creator = CreateBillInfoView(new_win)
        creator.pack(fill="both", expand=True)
        
        # Update save command to refresh list
        creator.save_button.configure(
            command=lambda: [
                creator.save_bill_info(),
                new_win.destroy(),
                self.load_bill_infos()
            ]
        )

    def delete_bill_info(self):
        """Delete selected bill"""
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Please select a bill to delete", "No Selection")
            return

        bill_id = self.tree.item(selected[0])['values'][0]
        
        if Messagebox.show_question(
            f"Delete bill #{bill_id}? This cannot be undone!",
            "Confirm Delete",
            parent=self
        ) == "No":
            return

        try:
            session = Session()
            bill = session.query(BillInfo).filter_by(id=bill_id).first()
            if bill:
                session.delete(bill)
                session.commit()
                self.load_bill_infos()
            session.close()
        except Exception as e:
            Messagebox.show_error(f"Error deleting bill: {str(e)}", "Delete Error")

    def print_bill_details(self):
        """Print detailed bill information including particulars"""
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Please select a bill to print", "No Selection")
            return

        bill_id = self.tree.item(selected[0])['values'][0]
        
        try:
            session = Session()
            # Get bill info
            bill = session.query(BillInfo).filter_by(id=bill_id).first()
            
            if not bill:
                Messagebox.show_error("Bill not found", "Error")
                return

            # Get shop details
            shop = session.query(ShopProfile).filter_by(id=bill.shop_id).first()
            
            # Get bill particulars
            particulars = session.query(BillParticular).filter_by(bill_id=bill_id).all()

            # Build printable content
            output = "\n" + "="*40 + "\n"
            output += f"BILL DETAILS - ID: {bill.id}\n"
            output += "="*40 + "\n"
            output += f"Shop: {shop.shop_name} ({shop.shop_no})\n"
            output += f"Bill Period: {bill.bill_month}/{bill.bill_year}\n"
            output += f"Bill Date: {bill.bill_date.strftime('%Y-%m-%d')}\n"
            output += "-"*40 + "\n"
            output += "PARTICULARS:\n"
            
            total_amount = 0.0
            for idx, particular in enumerate(particulars, 1):
                output += f"{idx}. {particular.bill_particular}\n"
                output += f"   Qty: {particular.bill_qty} {particular.bill_unit}\n"
                output += f"   Rate: ${particular.bill_rate:.2f}\n"
                output += f"   Amount: ${particular.sub_amount:.2f}\n"
                total_amount += float(particular.sub_amount)
            
            output += "-"*40 + "\n"
            output += f"Total Amount: ${total_amount:.2f}\n"
            output += f"Previous Due: ${bill.prev_due:.2f}\n"
            output += f"Status: {'Paid' if bill.status == 1 else 'Pending'}\n"
            output += "="*40 + "\n"
            
            # Show success message
            Messagebox.show_info(
                "Bill details printed to console\n(Implement physical printing here)",
                "Print Success"
            )
            
            session.close()
            
        except Exception as e:
            Messagebox.show_error(f"Error printing bill: {str(e)}", "Print Error")