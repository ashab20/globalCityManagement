import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_profile import ShopProfile
from models.shop_owner_profile import ShopOwnerProfile  # Assuming you have this model
from utils.database import Session
from ttkbootstrap.dialogs import Messagebox


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
        # ttk.Label(self, text="Create New Shop", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=(0, 20))

        # Shop Name
        ttk.Label(self, text="Shop Name:", bootstyle="primary").pack(anchor="w")
        self.shop_name_entry = ttk.Entry(self)
        self.shop_name_entry.pack(fill="x", pady=(0, 10))

        # Floor No
        ttk.Label(self, text="Floor No:", bootstyle="primary").pack(anchor="w")
        self.floor_no_entry = ttk.Entry(self)
        self.floor_no_entry.pack(fill="x", pady=(0, 10))

        # Shop No
        ttk.Label(self, text="Shop No:", bootstyle="primary").pack(anchor="w")
        self.shop_no_entry = ttk.Entry(self)
        self.shop_no_entry.pack(fill="x", pady=(0, 10))

        # Description
        ttk.Label(self, text="Description:", bootstyle="primary").pack(anchor="w")
        self.description_entry = ttk.Entry(self)
        self.description_entry.pack(fill="x", pady=(0, 10))
        
        # shop_size
        ttk.Label(self, text="Shop Size:", bootstyle="primary").pack(anchor="w")
        self.shop_size_entry = ttk.Entry(self)
        self.shop_size_entry.pack(fill="x", pady=(0, 10))

        # Rent Type
        ttk.Label(self, text="Rent Type:", bootstyle="primary").pack(anchor="w")
        self.rent_type_entry = ttk.Combobox(self, values=["Fixed", "Per Square Feet"], state="readonly")
        self.rent_type_entry.pack(fill="x", pady=(0, 10))

        # Rent Amount
        ttk.Label(self, text="Rent Amount:", bootstyle="primary").pack(anchor="w")
        self.rent_entry = ttk.Entry(self)
        self.rent_entry.pack(fill="x", pady=(0, 10))

        # Shop Owner
        ttk.Label(self, text="Shop Owner:", bootstyle="primary").pack(anchor="w")
        self.shop_owner_combobox = ttk.Combobox(self, state="readonly")
        self.shop_owner_combobox.pack(fill="x", pady=(0, 10))

        # Load shop owners into the combobox
        self.load_shop_owners()

        # Submit button
        ttk.Button(self, text="Create Shop", command=self.create_shop, bootstyle="primary", width=20).pack()
    
    def load_shop_owners(self):
        """Loads shop owners into the combobox."""
        try:
            session = Session()
            shop_owners = session.query(ShopOwnerProfile).all()
            session.close()

            print(shop_owners)

            # Populate the combobox with the owners' names and their IDs
            self.shop_owner_combobox['values'] = [owner.ownner_name for owner in shop_owners]  # Assuming `owner_name` is a field
            self.shop_owner_combobox.set('')  # Optionally set a default value

        except Exception as e:
            Messagebox.show_error(message=f"Error loading shop owners: {str(e)}", title="Error", parent=self)
    
    def create_shop(self):
        """Handle shop creation."""
        shop_name = self.shop_name_entry.get().strip()
        floor_no = self.floor_no_entry.get().strip()
        shop_no = self.shop_no_entry.get().strip()
        description = self.description_entry.get().strip()
        rent_amount = self.rent_entry.get().strip()

        rent_type = self.rent_type_entry.get().strip()
        shop_size = self.shop_size_entry.get().strip()

        shop_owner_name = self.shop_owner_combobox.get().strip()

        if not all([shop_name, floor_no, shop_no, description, shop_owner_name]):
            Messagebox.show_error(message="All fields except rent amount are required!", title="Validation Error", parent=self)
            return

        try:
            shop_size = float(shop_size)
        except ValueError:
            Messagebox.show_error(message="Shop size must be a number", title="Validation Error", parent=self)
            return

        try:
            rent = float(rent_amount) if rent_amount else None  # Convert rent to float if provided
        except ValueError:
            Messagebox.show_error(message="Rent amount must be a valid number!", title="Validation Error", parent=self)
            return

        # Calculate per_sqr_fit_amt based on rent type
        per_sqr_fit_amt = None
        if rent_type == "Per Square Feet":
            per_sqr_fit_amt = rent / shop_size
        elif rent_type == "Fixed":
            per_sqr_fit_amt = 0  # or some default value

        try:
            # Retrieve the shop owner id based on the selected owner name
            session = Session()
            shop_owner = session.query(ShopOwnerProfile).filter_by(ownner_name=shop_owner_name).first()  # Adjust this query if needed
            if not shop_owner:
                session.close()
                Messagebox.show_error(message="Selected shop owner does not exist!", title="Validation Error", parent=self)
                return

            # Create new shop profile
            new_shop = ShopProfile(
                shop_owner_id=shop_owner.id,  # Using the selected shop owner's ID
                floor_no=floor_no,
                shop_no=shop_no,
                shop_name=shop_name,
                descreption=description,
                rent_type=rent_type,
                shop_size=shop_size,
                per_sqr_fit_amt=per_sqr_fit_amt,
                rent_amout=rent,
                created_by=1  # This should be dynamically set based on the logged-in user
            )
            
            session.add(new_shop)
            session.commit()
            session.close()
            
            Messagebox.show_info(message="Shop created successfully!", title="Success", parent=self)
            
            # Clear form
            self.shop_name_entry.delete(0, "end")
            self.floor_no_entry.delete(0, "end")
            self.shop_no_entry.delete(0, "end")
            self.description_entry.delete(0, "end")
            self.rent_entry.delete(0, "end")
            self.shop_size_entry.delete(0, "end")
            self.rent_type_entry.delete(0, "end")
            self.shop_owner_combobox.set('')

        except Exception as e:
            Messagebox.show_error(message=f"Error creating shop: {str(e)}", title="Error", parent=self)
