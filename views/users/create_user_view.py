import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.user import User
from models.role import Role
from utils.database import Session


class CreateUserView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Create main container with padding and background
        self.main_frame = ttk.Frame(self, style="Content.TFrame", padding=20)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Creates the user creation form."""
        # Title
        title_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="Create New User",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack()
        
        # Form container
        form_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        form_frame.pack(fill="both", expand=True)
        
        # Username
        ttk.Label(
            form_frame,
            text="Username",
            font=("Helvetica", 10, "bold"),
            bootstyle="primary"
        ).pack(anchor="w")
        
        self.username_entry = ttk.Entry(
            form_frame,
            bootstyle="primary"
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password
        ttk.Label(
            form_frame,
            text="Password",
            font=("Helvetica", 10, "bold"),
            bootstyle="primary"
        ).pack(anchor="w")
        
        self.password_entry = ttk.Entry(
            form_frame,
            show="•",
            bootstyle="primary"
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        ttk.Label(
            form_frame,
            text="Email",
            font=("Helvetica", 10, "bold"),
            bootstyle="primary"
        ).pack(anchor="w")
        
        self.email_entry = ttk.Entry(
            form_frame,
            bootstyle="primary"
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Role
        ttk.Label(
            form_frame,
            text="Role",
            font=("Helvetica", 10, "bold"),
            bootstyle="primary"
        ).pack(anchor="w")
        
        # Get roles from database
        session = Session()
        roles = session.query(Role).all()
        session.close()
        
        # Create role selection frame
        role_frame = ttk.Frame(form_frame, style="Content.TFrame")
        role_frame.pack(fill="x", pady=(0, 20))
        
        self.role_var = ttk.StringVar()
        
        for role in roles:
            ttk.Radiobutton(
                role_frame,
                text=role.name,
                variable=self.role_var,
                value=str(role.id),
                bootstyle="primary-toolbutton"
            ).pack(side="left", padx=5)
        
        # Submit button
        button_frame = ttk.Frame(form_frame, style="Content.TFrame")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="Create User",
            command=self.create_user,
            bootstyle="primary",
            width=20
        ).pack(side="right")
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form,
            bootstyle="secondary",
            width=20
        ).pack(side="right", padx=10)
    
    def clear_form(self):
        """Clear all form fields."""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.role_var.set("")
    
    def create_user(self):
        """Handle user creation."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        role_id = int(self.role_var.get()) if self.role_var.get() else None
        
        if not all([username, password, email, role_id]):
            ttk.dialogs.Messagebox.show_error(
                message="All fields are required!",
                title="Validation Error",
                parent=self
            )
            return
        
        try:
            session = Session()
            
            # Check if username exists
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                session.close()
                ttk.dialogs.Messagebox.show_error(
                    message="Username already exists!",
                    title="Validation Error",
                    parent=self
                )
                return
            
            # Create new user
            new_user = User(
                username=username,
                password=password,
                email=email,
                role_id=role_id
            )
            
            session.add(new_user)
            session.commit()
            session.close()
            
            ttk.dialogs.Messagebox.show_info(
                message="User created successfully!",
                title="Success",
                parent=self
            )
            
            # Clear form
            self.clear_form()
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error creating user: {str(e)}",
                title="Error",
                parent=self
            )