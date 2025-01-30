import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.user import User
from werkzeug.security import check_password_hash
from PIL import Image, ImageTk
import os


class LoginView(ttk.Frame):
    def __init__(self, parent, on_login=None):
        super().__init__(parent)
        self.parent = parent
        self.on_login = on_login
        
        # Configure styles
        style = ttk.Style()
        style.configure("Login.TFrame", background="white")
        style.configure("Login.TLabel", background="white", font=("Helvetica", 10))
        style.configure("LoginTitle.TLabel", 
                       background="white", 
                       font=("Helvetica", 20, "bold"),
                       foreground="#4361ee")
        
        # Main container
        main_frame = ttk.Frame(self, style="Login.TFrame")
        main_frame.pack(fill="both", expand=True)
        
        # Center frame
        center_frame = ttk.Frame(main_frame, style="Login.TFrame", width=400)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo frame
        logo_frame = ttk.Frame(center_frame, style="Login.TFrame")
        logo_frame.pack(fill="x", pady=(0, 10))
        
        # Load and display logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'logo.png')
        logo_image = Image.open(logo_path)
        # Resize logo to 300x100
        logo_image = logo_image.resize((300, 100), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        
        ttk.Label(
            logo_frame,
            image=self.logo_photo,
            style="Login.TLabel"
        ).pack(anchor="center")

        # Company name
        ttk.Label(
            logo_frame,
            text="Global City Management",
            style="LoginTitle.TLabel"
        ).pack(anchor="center", pady=(10, 0))
        
        # Form frame
        form_frame = ttk.Frame(center_frame, style="Login.TFrame", padding=20)
        form_frame.pack(fill="x")
        
        # Username
        ttk.Label(
            form_frame,
            text="Username:",
            style="Login.TLabel"
        ).pack(fill="x", pady=(0, 5))
        
        self.username_entry = ttk.Entry(form_frame, width=40)
        self.username_entry.pack(pady=(0, 20))
        
        # Password
        ttk.Label(
            form_frame,
            text="Password:",
            style="Login.TLabel"
        ).pack(fill="x", pady=(0, 5))
        
        self.password_entry = ttk.Entry(form_frame, show="•", width=40)
        self.password_entry.pack(pady=(0, 30))
        
        # Error message
        self.error_label = ttk.Label(
            form_frame,
            text="",
            style="Login.TLabel",
            foreground="red",
            wraplength=350
        )
        self.error_label.pack(fill="x", pady=(0, 20))
        
        # Login button
        ttk.Button(
            form_frame,
            text="Login",
            command=self.login,
            bootstyle="primary",
            width=20,
            padding=10
        ).pack()
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Focus username entry
        self.username_entry.focus()
    
    def login(self):
        """Handle login attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.error_label.config(text="Please enter both username and password")
            return
        
        # Find user
        user = User.find_by_username(username)
        print(f"User: {user}")
        print(check_password_hash(user.password, password))
        # if not user or not check_password_hash(user.password, password):
        #     self.error_label.config(text="Invalid username or password")
        #     return
        
        # Clear error
        self.error_label.config(text="")
        
        # Call login callback
        if self.on_login:
            self.on_login()
    