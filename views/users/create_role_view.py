import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.role import Role
from utils.database import Session


class CreateRoleView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Creates the role creation form."""
        # Title
        ttk.Label(
            self,
            text="Create New Role",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Role Name
        ttk.Label(
            self,
            text="Role Name:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.name_entry = ttk.Entry(self)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Description
        ttk.Label(
            self,
            text="Description:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.description_text = ttk.Text(
            self,
            height=4,
            width=40,
            font=("Helvetica", 10)
        )
        self.description_text.pack(fill="x", pady=(0, 20))
        
        # Submit button
        ttk.Button(
            self,
            text="Create Role",
            command=self.create_role,
            bootstyle="primary",
            width=20
        ).pack()
    
    def create_role(self):
        """Handle role creation."""
        name = self.name_entry.get()
        description = self.description_text.get("1.0", "end-1c")
        
        if not name:
            ttk.dialogs.Messagebox.show_error(
                message="Role name is required!",
                title="Validation Error",
                parent=self
            )
            return
        
        try:
            session = Session()
            
            # Check if role exists
            existing_role = session.query(Role).filter_by(name=name).first()
            if existing_role:
                session.close()
                ttk.dialogs.Messagebox.show_error(
                    message="Role already exists!",
                    title="Validation Error",
                    parent=self
                )
                return
            
            # Create new role
            new_role = Role(
                name=name,
                description=description
            )
            
            session.add(new_role)
            session.commit()
            session.close()
            
            ttk.dialogs.Messagebox.show_info(
                message="Role created successfully!",
                title="Success",
                parent=self
            )
            
            # Clear form
            self.name_entry.delete(0, "end")
            self.description_text.delete("1.0", "end")
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error creating role: {str(e)}",
                title="Error",
                parent=self
            )
