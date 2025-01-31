import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.user import User
from utils.database import Session
import io
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog


class UserOptionsDialog(tk.Toplevel):
    def __init__(self, parent, user, session):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.session = session
        
        self.title(f"User Options: {user.login_id}")
        self.geometry("400x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(fill="both", expand=True)
        
        # User Avatar
        self.display_avatar()
        
        # User Details Section
        self.display_user_details()
        
        # Action Buttons
        self.create_action_buttons()
    
    def display_avatar(self):
        """Display user avatar"""
        avatar_frame = ttk.Frame(self.main_frame)
        avatar_frame.pack(pady=(0, 10))
        
        # Default avatar if no image
        if self.user.avatar:
            try:
                image = Image.open(io.BytesIO(self.user.avatar))
                image.thumbnail((200, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                avatar_label = ttk.Label(avatar_frame, image=photo)
                avatar_label.image = photo  # Keep a reference
                avatar_label.pack()
            except Exception:
                ttk.Label(avatar_frame, text="Avatar Not Available", bootstyle="secondary").pack()
        else:
            ttk.Label(avatar_frame, text="No Avatar", bootstyle="secondary").pack()
    
    def display_user_details(self):
        """Display comprehensive user details"""
        details_frame = ttk.Frame(self.main_frame)
        details_frame.pack(pady=(10, 20))
        
        details = [
            ("Username", self.user.login_id),
            ("Full Name", self.user.usr_full_name),
            ("Email", self.user.email),
            ("Phone", self.user.phone),
            ("Role", self.user.role.name if self.user.role else "No Role"),
            ("Status", "Active" if self.user.active_status == 1 else "Inactive")
        ]
        
        for label, value in details:
            row_frame = ttk.Frame(details_frame)
            row_frame.pack(fill="x", pady=5)
            
            ttk.Label(row_frame, text=f"{label}:", width=15, bootstyle="primary").pack(side="left")
            ttk.Label(row_frame, text=str(value), bootstyle="secondary").pack(side="left")
    
    def create_action_buttons(self):
        """Create action buttons for user management"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=(20, 0), fill="x")
        
        # Button configurations
        button_configs = [
            ("Edit User", self.edit_user, "primary"),
            ("Change Password", self.change_password, "warning"),
            ("Delete User", self.delete_user, "danger"),
            ("Toggle Status", self.toggle_user_status, "info")
        ]
        
        # Create buttons
        for label, command, style in button_configs:
            btn = ttk.Button(
                button_frame, 
                text=label, 
                command=command, 
                bootstyle=f"{style}-outline",
                width=20
            )
            btn.pack(pady=5)
    
    def edit_user(self):
        """Open edit user dialog with tabs"""
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Edit User: {self.user.login_id}")
        edit_window.geometry("600x800")
        
        # Notebook (Tabbed Interface)
        notebook = ttk.Notebook(edit_window)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # User Details Tab
        user_details_frame = ttk.Frame(notebook)
        notebook.add(user_details_frame, text="User Details")
        
        # Role Selection
        session = Session()
        try:
            # Get roles from database
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
                user_details_frame,
                text="Role:",
                font=("Helvetica", 12),  
                bootstyle="primary"
            ).pack(anchor="w", fill="x")
            
            # Extract role names for combobox
            role_names = [role.name for role in roles]
            
            role_var = ttk.StringVar(value=self.user.role.name if self.user.role else role_names[0])
            role_combobox = ttk.Combobox(
                user_details_frame, 
                textvariable=role_var,
                values=role_names,
                state="readonly",
                bootstyle="primary"
            )
            role_combobox.pack(fill="x", pady=(0, 15))
            role_combobox.configure(width=50)
        
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading roles: {str(e)}",
                title="Error",
                parent=edit_window
            )
        
        # Username (read-only)
        ttk.Label(
            user_details_frame,
            text="Username:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        username_entry = ttk.Entry(
            user_details_frame, 
            font=("Helvetica", 12)  
        )
        username_entry.insert(0, self.user.login_id)
        username_entry.configure(state="readonly")
        username_entry.pack(fill="x", pady=(0, 15))
        
        # Full Name
        ttk.Label(
            user_details_frame,
            text="Full Name:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        full_name_entry = ttk.Entry(
            user_details_frame, 
            font=("Helvetica", 12)  
        )
        full_name_entry.insert(0, self.user.usr_full_name)
        full_name_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        ttk.Label(
            user_details_frame,
            text="Email:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        email_entry = ttk.Entry(
            user_details_frame, 
            font=("Helvetica", 12)  
        )
        email_entry.insert(0, self.user.email)
        email_entry.pack(fill="x", pady=(0, 15))
        
        # Phone
        ttk.Label(
            user_details_frame,
            text="Phone:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        phone_entry = ttk.Entry(
            user_details_frame, 
            font=("Helvetica", 12)  
        )
        phone_entry.insert(0, self.user.phone)
        phone_entry.pack(fill="x", pady=(0, 15))
        
        # Password Tab
        password_frame = ttk.Frame(notebook)
        notebook.add(password_frame, text="Change Password")
        
        # Current Password
        ttk.Label(
            password_frame,
            text="Current Password:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        current_pwd_entry = ttk.Entry(
            password_frame, 
            show="*",
            font=("Helvetica", 12)  
        )
        current_pwd_entry.pack(fill="x", pady=(0, 15))
        
        # New Password
        ttk.Label(
            password_frame,
            text="New Password:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        new_pwd_entry = ttk.Entry(
            password_frame, 
            show="*",
            font=("Helvetica", 12)  
        )
        new_pwd_entry.pack(fill="x", pady=(0, 15))
        
        # Confirm New Password
        ttk.Label(
            password_frame,
            text="Confirm New Password:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        ).pack(anchor="w", fill="x")
        confirm_pwd_entry = ttk.Entry(
            password_frame, 
            show="*",
            font=("Helvetica", 12)  
        )
        confirm_pwd_entry.pack(fill="x", pady=(0, 15))
        
        # Avatar Tab
        avatar_frame = ttk.Frame(notebook)
        notebook.add(avatar_frame, text="Avatar")
        
        # Current Avatar Display
        current_avatar_label = ttk.Label(
            avatar_frame,
            text="Current Avatar:",
            font=("Helvetica", 12),  
            bootstyle="primary"
        )
        current_avatar_label.pack(anchor="w", fill="x")
        
        # Display current avatar
        avatar_display = ttk.Label(avatar_frame)
        if self.user.avatar:
            try:
                image = Image.open(io.BytesIO(self.user.avatar))
                image.thumbnail((300, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                avatar_display.configure(image=photo)
                avatar_display.image = photo  # Keep a reference
            except Exception:
                avatar_display.configure(text="Avatar Not Available")
        else:
            avatar_display.configure(text="No Avatar")
        avatar_display.pack(pady=(0, 15))
        
        # Avatar selection button
        avatar_button = ttk.Button(
            avatar_frame,
            text="Select New Avatar",
            bootstyle="primary-outline",
            command=lambda: self.select_new_avatar(avatar_display)
        )
        avatar_button.pack(fill="x", pady=(0, 20))
        
        # Save Button
        def save_changes():
            try:
                # Update role
                selected_role_name = role_var.get()
                selected_role = session.query(UserRole).filter_by(name=selected_role_name).first()
                self.user.role = selected_role
                
                # Update user details
                self.user.usr_full_name = full_name_entry.get()
                self.user.email = email_entry.get()
                self.user.phone = phone_entry.get()
                
                # Password change
                current_pwd = current_pwd_entry.get()
                new_pwd = new_pwd_entry.get()
                confirm_pwd = confirm_pwd_entry.get()
                
                if current_pwd or new_pwd or confirm_pwd:
                    # Validate current password
                    if not self.user.check_password(current_pwd):
                        messagebox.showerror("Error", "Current password is incorrect")
                        return
                    
                    # Validate new password
                    if new_pwd != confirm_pwd:
                        messagebox.showerror("Error", "New passwords do not match")
                        return
                    
                    # Update password
                    self.user.set_password(new_pwd)
                
                # Commit changes
                session.commit()
                
                ttk.dialogs.Messagebox.show_info("User updated successfully!", title="Success")
                edit_window.destroy()
                self.destroy()
                self.parent.load_users()
            
            except Exception as e:
                ttk.dialogs.Messagebox.show_error(f"Error updating user: {str(e)}", title="Error")
        
        # Save Changes Button
        save_button = ttk.Button(
            edit_window,
            text="Save Changes",
            bootstyle="success",
            command=save_changes
        )
        save_button.pack(side="bottom", pady=10)
    
    def select_new_avatar(self, avatar_display):
        """Select a new avatar image"""
        try:
            # Open file dialog to select image
            file_path = filedialog.askopenfilename(
                title="Select Avatar",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Read image file
                with open(file_path, 'rb') as file:
                    avatar_bytes = file.read()
                
                # Validate file size (e.g., max 5MB)
                if len(avatar_bytes) > 5 * 1024 * 1024:
                    messagebox.showerror("Error", "Avatar file is too large. Maximum size is 5MB.")
                    return
                
                # Update user's avatar
                self.user.avatar = avatar_bytes
                
                # Display new avatar
                image = Image.open(io.BytesIO(avatar_bytes))
                image.thumbnail((300, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                avatar_display.configure(image=photo)
                avatar_display.image = photo  # Keep a reference
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select avatar: {str(e)}")
        finally:
            # Ensure session is closed
            if 'session' in locals():
                session.close()
    
    def change_password(self):
        """Open change password dialog"""
        change_pwd_window = tk.Toplevel(self)
        change_pwd_window.title(f"Change Password: {self.user.login_id}")
        change_pwd_window.geometry("400x300")
        
        # Current Password
        ttk.Label(change_pwd_window, text="Current Password:").pack()
        current_pwd_entry = ttk.Entry(change_pwd_window, show="*")
        current_pwd_entry.pack()
        
        # New Password
        ttk.Label(change_pwd_window, text="New Password:").pack()
        new_pwd_entry = ttk.Entry(change_pwd_window, show="*")
        new_pwd_entry.pack()
        
        # Confirm New Password
        ttk.Label(change_pwd_window, text="Confirm New Password:").pack()
        confirm_pwd_entry = ttk.Entry(change_pwd_window, show="*")
        confirm_pwd_entry.pack()
        
        # Save button
        def save_new_password():
            current_pwd = current_pwd_entry.get()
            new_pwd = new_pwd_entry.get()
            confirm_pwd = confirm_pwd_entry.get()
            
            # Validate current password
            if not self.user.check_password(current_pwd):
                messagebox.showerror("Error", "Current password is incorrect")
                return
            
            # Validate new password
            if new_pwd != confirm_pwd:
                messagebox.showerror("Error", "New passwords do not match")
                return
            
            try:
                # Update password
                self.user.set_password(new_pwd)
                self.session.commit()
                ttk.dialogs.Messagebox.show_info("Password changed successfully!", title="Success")
                change_pwd_window.destroy()
            except Exception as e:
                ttk.dialogs.Messagebox.show_error(f"Error changing password: {str(e)}", title="Error")
        
        ttk.Button(change_pwd_window, text="Change Password", command=save_new_password).pack(pady=10)
    
    def delete_user(self):
        """Delete user with confirmation"""
        if ttk.dialogs.Messagebox.show_question(
            "Are you sure you want to delete this user?", 
            title="Confirm Deletion", 
            parent=self
        ) == "Yes":
            try:
                self.session.delete(self.user)
                self.session.commit()
                ttk.dialogs.Messagebox.show_info("User deleted successfully.", title="Success")
                self.destroy()
                self.parent.load_users()
            except Exception as e:
                ttk.dialogs.Messagebox.show_error(f"Error deleting user: {str(e)}", title="Error")
    
    def toggle_user_status(self):
        """Toggle user active status"""
        try:
            # Toggle active status
            self.user.active_status = 0 if self.user.active_status == 1 else 1
            self.session.commit()
            
            status_text = "activated" if self.user.active_status == 1 else "deactivated"
            ttk.dialogs.Messagebox.show_info(f"User {status_text} successfully.", title="Success")
            
            self.destroy()
            self.parent.load_users()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(f"Error toggling user status: {str(e)}", title="Error")


class ListUserView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        # Create user list
        self.create_user_list()
    
    def create_user_list(self):
        """Creates the user list view."""
        # Create treeview with comprehensive columns
        columns = ("Serial", "Username", "Full Name", "Email", "Phone", "Avatar", "Role", "Status")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )
        
        # Configure columns
        self.tree.heading("Serial", text="Serial")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Full Name", text="Full Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Avatar", text="Avatar")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        
        # Column widths and alignments
        column_widths = {
            "Serial": 50,
            "Username": 100,
            "Full Name": 150,
            "Email": 200,
            "Phone": 120,
            "Avatar": 100,
            "Role": 100,
            "Status": 80
        }
        
        for col, width in column_widths.items():
            self.tree.column(col, width=width, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind left-click to show user options
        self.tree.bind("<Button-1>", self.show_user_options)
        
        # Load users
        self.load_users()
        
        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_users,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))
    
    def show_user_options(self, event):
        """Show user options dialog on left-click"""
        # Get the row under the mouse cursor
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        
        # Get username from the selected row
        username = self.tree.item(iid)['values'][1]
        
        try:
            # Create a new session
            session = Session()
            
            # Query user
            user = session.query(User).filter_by(login_id=username).first()
            
            if user:
                # Open user options dialog
                UserOptionsDialog(self, user, session)
            else:
                ttk.dialogs.Messagebox.show_warning("User not found.", title="Warning")
        
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(f"Error loading user: {str(e)}", title="Error")
    
    def load_users(self):
        """Load users from database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            session = Session()
            users = session.query(User).all()
            
            # Store references to prevent garbage collection
            self.avatar_images = []
            
            for index, user in enumerate(users, 1):
                # Process avatar
                avatar_photo = None
                if user.avatar:
                    try:
                        # Convert bytes to PIL Image
                        image = Image.open(io.BytesIO(user.avatar))
                        
                        # Resize image to fit in the column
                        image.thumbnail((80, 80), Image.LANCZOS)
                        
                        # Convert to PhotoImage
                        avatar_photo = ImageTk.PhotoImage(image)
                        self.avatar_images.append(avatar_photo)
                    except Exception:
                        avatar_photo = None
                
                # Determine status text
                status_text = "Active" if user.active_status == 1 else "Inactive"
                
                # Insert row
                item = self.tree.insert(
                    "",
                    "end",
                    values=(
                        index, 
                        user.login_id,
                        user.usr_full_name,
                        user.email,
                        user.phone,
                        user.avatar,
                        user.role.name if user.role else "No Role",
                        status_text
                    )
                )
                
                # Add avatar image if available
                if avatar_photo:
                    self.tree.set(item, "Avatar", "")
                    self.tree.item(item, image=avatar_photo)
            
            session.close()
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading users: {str(e)}",
                title="Error",
                parent=self
            )
