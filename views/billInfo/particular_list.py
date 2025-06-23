import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from sqlalchemy.orm import sessionmaker
from models.particular import Particular
from utils.database import Session
from views.billInfo.create_particular import CreateParticularView
class ParticularListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self, 
            columns=("Particular Name", "Unit"), 
            show="headings"
        )
        
        # Define column headings
        self.tree.heading("Particular Name", text="Particular Name")
        self.tree.heading("Unit", text="Unit")
        
        # Set column widths
        self.tree.column("Particular Name", width=150)
        self.tree.column("Unit", width=150)
        
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
        ttk.Button(button_frame, text="Edit", command=self.edit_particular, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_particular, bootstyle="danger").pack(side="left", padx=5)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_particular)
        
        # Load initial data
        self.load_particulars()
    
    def load_particulars(self):
        """Load particulars from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        session = Session()
        try:
            particulars = session.query(Particular).all()
            
            for particular in particulars:
                
                # Insert into treeview
                item = self.tree.insert("", "end", values=(
                    particular.name,
                    particular.unit
                ), tags=(particular.id,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load particulars: {str(e)}")
        finally:
            session.close()
    
    def edit_particular(self, event=None):
        """Open edit window for selected particular."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a particular to edit.")
            return
        
        # Get the particular ID from the item's tag
        particular_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            particular = session.query(Particular).filter_by(id=particular_id).first()
            
            if particular:
                # Create a new window for editing
                edit_window = ttk.Toplevel(title="Edit Particular")
                edit_window.geometry("500x400")
                
                # Create edit view
                edit_view = CreateParticularView(edit_window, existing_particular=particular)
                edit_view.pack(fill="both", expand=True)
                
                # Add a callback to refresh list after editing
                def on_save():
                    self.load_particulars()
                    edit_window.destroy()
                
                edit_view.save_button.config(command=on_save)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load particular for editing: {str(e)}")
        finally:
            session.close()
    
    def delete_particular(self):
        """Delete the selected particular."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a particular to delete.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this particular?")
        if not confirm:
            return
        
        # Get the particular ID from the item's tag
        particular_id = self.tree.item(selected_item[0], "tags")[0]
        
        session = Session()
        try:
            particular = session.query(Particular).filter_by(id=particular_id).first()
            
            if particular:
                session.delete(particular)
                session.commit()
                
                # Refresh the list
                self.load_particulars()
                messagebox.showinfo("Success", "Particular deleted successfully.")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Could not delete particular: {str(e)}")
        finally:
            session.close()
