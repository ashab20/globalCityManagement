import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from sqlalchemy.orm import sessionmaker
from models.UtilitySetting import UtilitySetting
from utils.database import Session
from views.utilities.create_utilities import CreateUtilitySettingView

class ListUtilitiesView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self, 
            columns=("Utility Name", "Rate", "Remarks"), 
            show="headings"
        )
        
        # Define column headings
        self.tree.heading("Utility Name", text="Utility Name")
        self.tree.heading("Rate", text="Rate")
        self.tree.heading("Remarks", text="Remarks")
        
        # Set column widths
        self.tree.column("Utility Name", width=150)
        self.tree.column("Rate", width=100)
        self.tree.column("Remarks", width=100)
        
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
        ttk.Button(button_frame, text="Edit", command=self.edit_utility, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_utility, bootstyle="danger").pack(side="left", padx=5)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_utility)
        
        # Load initial data
        self.load_utilities()
    
    def load_utilities(self):
        """Load utility settings from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        session = Session()
        try:
            utilities = session.query(UtilitySetting).all()
            
            for utility in utilities:
                # Convert status to readable text
                # status_text = "Active" if str(utility.status) == "1" else "Inactive"
                
                # Insert into treeview
                item = self.tree.insert("", "end", values=(
                    utility.utility_name,
                    utility.utility_rate,
                    utility.remarks
                ), tags=(utility.id,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load utilities: {str(e)}")
        finally:
            session.close()
    
    def edit_utility(self, event=None):
        """Open edit window for selected utility."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a utility to edit.")
            return
        
        # Get the utility ID from the item's tag
        utility_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            utility = session.query(UtilitySetting).filter_by(id=utility_id).first()
            
            if utility:
                # Create a new window for editing
                edit_window = ttk.Toplevel(title="Edit Utility")
                edit_window.geometry("500x400")
                
                # Create edit view
                edit_view = CreateUtilitySettingView(edit_window, existing_utility=utility)
                edit_view.pack(fill="both", expand=True)
                
                # Add a callback to refresh list after editing
                def on_save():
                    self.load_utilities()
                    edit_window.destroy()
                
                edit_view.save_button.config(command=on_save)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load utility for editing: {str(e)}")
        finally:
            session.close()
    
    def delete_utility(self):
        """Delete the selected utility."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a utility to delete.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this utility?")
        if not confirm:
            return
        
        # Get the utility ID from the item's tag
        utility_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            utility = session.query(UtilitySetting).filter_by(id=utility_id).first()
            
            if utility:
                session.delete(utility)
                session.commit()
                
                # Refresh the list
                self.load_utilities()
                messagebox.showinfo("Success", "Utility deleted successfully.")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Could not delete utility: {str(e)}")
        finally:
            session.close()
