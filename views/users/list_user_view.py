import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.user import User
from utils.database import Session


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
        # Title
        ttk.Label(
            self,
            text="User List",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Create treeview
        columns = ("ID", "Username", "Email", "Role")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Role")
        
        self.tree.column("ID", width=50)
        self.tree.column("Username", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Role", width=150)
        
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
    
    def load_users(self):
        """Load users from database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            session = Session()
            users = session.query(User).all()
            
            for user in users:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        user.id,
                        user.username,
                        user.email,
                        user.role.name if user.role else "No Role"
                    )
                )
            
            session.close()
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading users: {str(e)}",
                title="Error",
                parent=self
            )
