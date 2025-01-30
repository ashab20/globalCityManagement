import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop import Shop
from utils.database import Session


class CreateShopView(ttk.Frame):
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
        """Creates the shop creation form."""
        # Title
        ttk.Label(
            self,
            text="Create New Shop",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Shop Name
        ttk.Label(
            self,
            text="Shop Name:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.name_entry = ttk.Entry(self)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Address
        ttk.Label(
            self,
            text="Address:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.address_entry = ttk.Entry(self)
        self.address_entry.pack(fill="x", pady=(0, 10))
        
        # Phone
        ttk.Label(
            self,
            text="Phone:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.pack(fill="x", pady=(0, 10))
        
        # Email
        ttk.Label(
            self,
            text="Email:",
            bootstyle="primary"
        ).pack(anchor="w")
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack(fill="x", pady=(0, 20))
        
        # Submit button
        ttk.Button(
            self,
            text="Create Shop",
            command=self.create_shop,
            bootstyle="primary",
            width=20
        ).pack()
    
    def create_shop(self):
        """Handle shop creation."""
        name = self.name_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        
        if not all([name, address, phone]):
            ttk.dialogs.Messagebox.show_error(
                message="Name, address and phone are required!",
                title="Validation Error",
                parent=self
            )
            return
        
        try:
            session = Session()
            
            # Check if shop exists
            existing_shop = session.query(Shop).filter_by(name=name).first()
            if existing_shop:
                session.close()
                ttk.dialogs.Messagebox.show_error(
                    message="Shop already exists!",
                    title="Validation Error",
                    parent=self
                )
                return
            
            # Create new shop
            new_shop = Shop(
                name=name,
                address=address,
                phone=phone,
                email=email
            )
            
            session.add(new_shop)
            session.commit()
            session.close()
            
            ttk.dialogs.Messagebox.show_info(
                message="Shop created successfully!",
                title="Success",
                parent=self
            )
            
            # Clear form
            self.name_entry.delete(0, "end")
            self.address_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.email_entry.delete(0, "end")
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error creating shop: {str(e)}",
                title="Error",
                parent=self
            )
