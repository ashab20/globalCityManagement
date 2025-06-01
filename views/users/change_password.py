import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.user import User
from utils.database import Session


class ChangePasswordView(ttk.Frame):
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
            text="Change Password",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Role Name
        ttk.Label(
            self,
            text="Old Password:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.old_password_entry = ttk.Entry(self)
        self.old_password_entry.pack(fill="x", pady=(0, 10))
        
        # Description
        ttk.Label(
            self,
            text="New Password:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.new_password_entry = ttk.Entry(
            self,
            height=4,
            width=40,
            font=("Helvetica", 10)
        )
        self.new_password_entry.pack(fill="x", pady=(0, 20))
        
        # Submit button
        ttk.Button(
            self,
            text="Change Password",
            command=self.change_password,
            bootstyle="primary",
            width=20
        ).pack()
    
    def change_password(self):
        """Handle role creation."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        
        if not old_password:
            ttk.dialogs.Messagebox.show_error(
                message="Old password is required!",
                title="Validation Error",
                parent=self
            )
            return
        
        try:
            session = Session()
            
            # Check if role exists
            existing_role = session.query(User).filter_by(password=old_password).first()
            if existing_role:
                session.close()
                ttk.dialogs.Messagebox.show_error(
                    message="Role already exists!",
                    title="Validation Error",
                    parent=self
                )
                return
            
            # Create new role
            user = User(
                password=new_password
            )
            
            session.add(user)
            session.commit()
            session.close()
            
            ttk.dialogs.Messagebox.show_info(
                message="Password changed successfully!",
                title="Success",
                parent=self
            )
            
            # Clear form
            self.old_password_entry.delete(0, "end")
            self.new_password_entry.delete("1.0", "end")
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error changing password: {str(e)}",
                title="Error",
                parent=self
            )
