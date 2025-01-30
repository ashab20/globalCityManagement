import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from utils.database import Session
from models.user import User
from models.role import Role


class ListRoleView(ttk.Frame):
    def __init__(self, root, on_back_callback=None):
        super().__init__(root, bootstyle="light", padding=20)
        
        self.root = root
        self.on_back_callback = on_back_callback
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create centered container
        container = ttk.Frame(self, bootstyle="light")
        container.pack(expand=True)
        
        # Title
        title_label = ttk.Label(
            container,
            text="Role List",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Create content frame
        content_frame = ttk.Frame(container, bootstyle="light")
        content_frame.pack(fill="both", expand=True, padx=20)
        
        # Create toolbar
        toolbar = ttk.Frame(content_frame, bootstyle="light")
        toolbar.pack(fill="x", pady=(0, 10))
        
        # Refresh button
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_table,
            bootstyle="primary",
            width=10
        ).pack(side="left")
        
        # Back button
        if self.on_back_callback:
            ttk.Button(
                toolbar,
                text="Back",
                command=self.on_back_callback,
                bootstyle="link",
                width=10
            ).pack(side="right")
        
        # Create table
        self.create_table(content_frame)
        
    def create_table(self, parent):
        coldata = [
            {"text": "ID", "stretch": False, "width": 50},
            {"text": "Role Name", "stretch": True, "width": 150},
            {"text": "Email", "stretch": True, "width": 200},
            {"text": "Phone", "stretch": False, "width": 120},
            {"text": "Role", "stretch": True, "width": 100}
        ]
        
        self.table = Tableview(
            master=parent,
            coldata=coldata,
            rowdata=self.get_users(),
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            stripecolor=("white", "#f0f0f0"),
            height=15
        )
        self.table.pack(fill=BOTH, expand=YES, pady=5)
    
    def get_users(self):
        """Get all users from database"""
        session = Session()
        try:
            users = session.query(User).all()
            user_data = []
            
            for user in users:
                role = session.query(Role).filter_by(id=user.role_id).first()
                role_name = role.name if role else "No Role"
                
                user_data.append((
                    user.id,
                    user.username,
                    user.email,
                    user.phone,
                    role_name
                ))
            
            return user_data
            
        except Exception as e:
            print(f"Error loading users: {str(e)}")
            return []
        finally:
            session.close()
    
    def refresh_table(self):
        """Refresh the table data"""
        self.table.destroy()
        self.create_table(self.winfo_children()[0].winfo_children()[1])
