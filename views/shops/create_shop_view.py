import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_profile import ShopProfile
from models.shop_owner_profile import ShopOwnerProfile  # Assuming you have this model
from utils.database import Session
from ttkbootstrap.dialogs import Messagebox


class CreateShopView(ttk.Frame):
    def __init__(self, parent, existing_shop=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_shop = existing_shop
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Create form
        self.create_form()
    
    def load_shop_owners(self):
        """Loads shop owners into the combobox."""
        try:
            session = Session()
            shop_owners = session.query(ShopOwnerProfile).all()
            
            # Populate the combobox with the owners' names
            owner_names = [owner.ownner_name for owner in shop_owners]
            self.shop_owner_combobox['values'] = owner_names
            
            # If editing an existing shop, set the current shop owner
            if self.existing_shop:
                # Find the owner name for the current shop
                current_owner = session.query(ShopOwnerProfile).filter_by(id=self.existing_shop.shop_owner_id).first()
                if current_owner:
                    self.shop_owner_combobox.set(current_owner.ownner_name)
            
            session.close()

        except Exception as e:
            Messagebox.show_error(message=f"Error loading shop owners: {str(e)}", title="Error", parent=self)
    
    def create_form(self):
        """Creates the shop creation form."""
        # Create a main container frame with padding
        form_frame = ttk.Frame(self, padding=(20, 10))
        form_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            form_frame, 
            text="Create/Update Shop", 
            font=("Helvetica", 16, "bold"), 
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20), anchor="center")

        # Styling for labels and entries
        label_style = {"bootstyle": "primary", "font": ("Helvetica", 10)}
        entry_style = {"font": ("Helvetica", 10)}

        # Shop Name
        ttk.Label(form_frame, text="Shop Name:", **label_style).pack(anchor="w")
        self.shop_name_entry = ttk.Entry(form_frame, **entry_style)
        self.shop_name_entry.pack(fill="x", pady=(0, 10))

        # Floor No
        ttk.Label(form_frame, text="Floor No:", **label_style).pack(anchor="w")
        self.floor_no_entry = ttk.Entry(form_frame, **entry_style)
        self.floor_no_entry.pack(fill="x", pady=(0, 10))

        # Shop No
        ttk.Label(form_frame, text="Shop No:", **label_style).pack(anchor="w")
        self.shop_no_entry = ttk.Entry(form_frame, **entry_style)
        self.shop_no_entry.pack(fill="x", pady=(0, 10))

        # Description
        ttk.Label(form_frame, text="Description:", **label_style).pack(anchor="w")
        self.description_entry = ttk.Entry(form_frame, **entry_style)
        self.description_entry.pack(fill="x", pady=(0, 10))
        
        # Shop Size
        ttk.Label(form_frame, text="Shop Size:", **label_style).pack(anchor="w")
        self.shop_size_entry = ttk.Entry(form_frame, **entry_style)
        self.shop_size_entry.pack(fill="x", pady=(0, 10))

        # Rent Type
        ttk.Label(form_frame, text="Rent Type:", **label_style).pack(anchor="w")
        self.rent_type_entry = ttk.Combobox(
            form_frame, 
            values=["Fixed", "Per Square Feet"], 
            state="readonly",
            **entry_style
        )
        self.rent_type_entry.pack(fill="x", pady=(0, 10))

        # Rent Amount
        ttk.Label(form_frame, text="Rent Amount:", **label_style).pack(anchor="w")
        self.rent_entry = ttk.Entry(form_frame, **entry_style)
        self.rent_entry.pack(fill="x", pady=(0, 10))

        # Shop Owner
        ttk.Label(form_frame, text="Shop Owner:", **label_style).pack(anchor="w")
        self.shop_owner_combobox = ttk.Combobox(
            form_frame, 
            state="readonly",
            **entry_style
        )
        self.shop_owner_combobox.pack(fill="x", pady=(0, 10))

        # Load shop owners into the combobox
        self.load_shop_owners()

        # Pre-fill data if editing an existing shop
        if self.existing_shop:
            self.shop_name_entry.insert(0, self.existing_shop.shop_name)
            self.floor_no_entry.insert(0, self.existing_shop.floor_no)
            self.shop_no_entry.insert(0, self.existing_shop.shop_no)
            self.description_entry.insert(0, self.existing_shop.descreption)
            self.shop_size_entry.insert(0, str(self.existing_shop.shop_size))
            self.rent_type_entry.set(self.existing_shop.rent_type)
            self.rent_entry.insert(0, str(self.existing_shop.rent_amout))

        # Submit button with clear styling
        submit_text = "Create Shop" if not self.existing_shop else "Update Shop"
        submit_command = self.create_shop
        self.save_button = ttk.Button(
            form_frame, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="primary-outline",
            width=20
        )
        self.save_button.pack(pady=(10, 0))
    
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

            if self.existing_shop:
                # Update existing shop
                self.existing_shop.shop_name = shop_name
                self.existing_shop.floor_no = floor_no
                self.existing_shop.shop_no = shop_no
                self.existing_shop.descreption = description
                self.existing_shop.rent_type = rent_type
                self.existing_shop.shop_size = shop_size
                self.existing_shop.per_sqr_fit_amt = per_sqr_fit_amt
                self.existing_shop.rent_amout = rent
                self.existing_shop.shop_owner_id = shop_owner.id
                session.add(self.existing_shop)
            else:
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
            
            if self.existing_shop:
                Messagebox.show_info(message="Shop updated successfully!", title="Success", parent=self)
            else:
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
