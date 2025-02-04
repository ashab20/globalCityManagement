import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import base64
import os

from models.user import User
from models.user_role import UserRole
from utils.database import Session
from werkzeug.security import generate_password_hash


class CreateUserView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(20, 10))
        self.parent = parent
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Create form
        self.create_form()
    
    def create_form(self):
        """Creates the user creation form."""
        # Create a container frame to control width and center the form
        form_container = ttk.Frame(self)
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Inner frame to center the content
        inner_frame = ttk.Frame(form_container)
        inner_frame.pack(expand=True, anchor="center")

        # Get roles from database
        session = Session()
        try:
            # Ensure at least one role exists
            roles = session.query(UserRole).all()
            if not roles:
                # Create default roles if none exist
                default_roles = ["Admin", "User"]
                for role_name in default_roles:
                    role = UserRole(name=role_name)
                    session.add(role)
                session.commit()
                roles = session.query(UserRole).all()
            
            # Role selection
            ttk.Label(
                inner_frame,
                text="Role:",
                font=("Helvetica", 12),  
                bootstyle="primary"
            ).pack(anchor="w", fill="x")
            
            # Extract role names for combobox
            role_names = [role.name for role in roles]
            
            role_var = ttk.StringVar()
            self.role_combobox = ttk.Combobox(
                inner_frame, 
                textvariable=role_var,
                values=role_names,
                state="readonly",
                bootstyle="primary"
            )
            self.role_combobox.pack(fill="x", pady=(0, 15))
            self.role_combobox.configure(width=50)
            
            # Set default selection to first role
            if role_names:
                self.role_combobox.set(role_names[0])
        
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading roles: {str(e)}",
                title="Error",
                parent=self
            )
        finally:
            session.close()

        # Username
        ttk.Label(
            inner_frame,
            text="Username:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        self.username_entry = ttk.Entry(
            inner_frame, 
            font=("Helvetica", 12)  
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        self.username_entry.configure(width=50)
        
        # Full Name
        ttk.Label(
            inner_frame,
            text="Full Name:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        self.full_name_entry = ttk.Entry(
            inner_frame, 
            font=("Helvetica", 12)  
        )
        self.full_name_entry.pack(fill="x", pady=(0, 15))
        self.full_name_entry.configure(width=50)
        
        # Email
        ttk.Label(
            inner_frame,
            text="Email:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        self.email_entry = ttk.Entry(
            inner_frame, 
            font=("Helvetica", 12)  
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        self.email_entry.configure(width=50)
        
        # Phone
        ttk.Label(
            inner_frame,
            text="Phone:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        self.phone_entry = ttk.Entry(
            inner_frame, 
            font=("Helvetica", 12)  
        )
        self.phone_entry.pack(fill="x", pady=(0, 15))
        self.phone_entry.configure(width=50)
        
        # Password Frame
        password_frame = ttk.Frame(inner_frame)
        password_frame.pack(fill="x", pady=(0, 15))
        
        # Password Label
        ttk.Label(
            password_frame,
            text="Password:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(side="left", anchor="w")
        
        # Password Entry
        self.password_entry = ttk.Entry(
            inner_frame, 
            show="*",
            font=("Helvetica", 12)  
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        self.password_entry.configure(width=50)
        
        # Confirm Password Frame
        confirm_password_frame = ttk.Frame(inner_frame)
        confirm_password_frame.pack(fill="x", pady=(0, 15))
        
        # Confirm Password Label
        ttk.Label(
            confirm_password_frame,
            text="Confirm Password:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(side="left", anchor="w")
        
        # Confirm Password Entry
        self.confirm_password_entry = ttk.Entry(
            inner_frame, 
            show="*",
            font=("Helvetica", 12)  
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 15))
        self.confirm_password_entry.configure(width=50)
        
        # Avatar
        ttk.Label(
            inner_frame,
            text="Avatar:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        
        # Avatar selection button
        self.avatar_button = ttk.Button(
            inner_frame,
            text="Select Avatar",
            bootstyle="primary-outline",
            command=self.select_avatar
        )
        self.avatar_button.pack(fill="x", pady=(0, 20))
        
        # Store avatar as bytes
        self.avatar_bytes = None
        
        # Submit button
        ttk.Button(
            inner_frame,
            text="Create User",
            command=self.create_user,
            bootstyle="primary"
        ).pack(pady=(0, 20))
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
    
    def toggle_confirm_password_visibility(self):
        """Toggle confirm password visibility"""
        if self.show_confirm_password_var.get():
            self.confirm_password_entry.configure(show="")
        else:
            self.confirm_password_entry.configure(show="*")
    
    def select_avatar(self):
        """Open file dialog to select avatar image"""
        file_path = filedialog.askopenfilename(
            title="Select Avatar",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                # Read image and convert to bytes
                with open(file_path, "rb") as image_file:
                    self.avatar_bytes = image_file.read()
                
                # Update button text
                self.avatar_button.configure(text=os.path.basename(file_path))
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image: {str(e)}")
    
    def create_user(self):
        """Create a new user"""
        # Validate inputs
        username = self.username_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        role_name = self.role_combobox.get()
        
        # Input validation
        if not all([username, full_name, email, phone, password, role_name]):
            ttk.dialogs.Messagebox.show_error(
                message="All fields are required!",
                title="Validation Error",
                parent=self
            )
            return
        
        if password != confirm_password:
            ttk.dialogs.Messagebox.show_error(
                message="Passwords do not match!",
                title="Validation Error",
                parent=self
            )
            return
        
        # Get role ID
        session = Session()
        try:
            # Check if username exists
            existing_user = session.query(User).filter_by(login_id=username).first()
            if existing_user:
                session.close()
                ttk.dialogs.Messagebox.show_error(
                    message="Username already exists!",
                    title="Validation Error",
                    parent=self
                )
                return
            
            role = session.query(UserRole).filter_by(name=role_name).first()
            if not role:
                ttk.dialogs.Messagebox.show_error(
                    message="Selected role does not exist!",
                    title="Validation Error",
                    parent=self
                )
                return
            
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Get logged in user's ID (if available)
            current_user_id = None
            try:
                # Assuming there's a way to get the current logged-in user
                # This might need to be adjusted based on your actual authentication mechanism
                current_user_id = getattr(self.parent, 'current_user_id', None)
            except Exception:
                pass
            
            # Create user
            new_user = User(
                login_id=username,
                usr_full_name=full_name,
                email=email,
                phone=phone,
                password=hashed_password,
                role_id=role.id,
                avatar=self.avatar_bytes if hasattr(self, 'avatar_bytes') else None,
                ptext=password,  # Store plaintext password temporarily
                created_by=current_user_id,  # Set created by logged in user
                update_by=None,
                active_status=1
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
            self.username_entry.delete(0, "end")
            self.full_name_entry.delete(0, "end")
            self.email_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            self.role_combobox.set("")
            self.avatar_button.configure(text="Select Avatar")
            if hasattr(self, 'avatar_bytes'):
                del self.avatar_bytes
            
        except Exception as e:
            session.rollback()
            ttk.dialogs.Messagebox.show_error(
                message=f"Error creating user: {str(e)}",
                title="Error",
                parent=self
            )