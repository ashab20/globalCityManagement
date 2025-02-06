import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, IntVar
from sqlalchemy.orm import sessionmaker
from models.shop_allocation import ShopAllocation
from models.shop_profile import ShopProfile
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session


class CreateShopAllocationView(ttk.Frame):
    def __init__(self, parent, existing_allocation=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_allocation = existing_allocation

        # StringVars for input fields
        self.shop_profile_id = StringVar()
        self.renter_profile_id = StringVar()
        self.from_year = StringVar()
        self.from_month = StringVar()
        self.to_year = StringVar()
        self.to_month = StringVar()
        self.close_status = IntVar(value=0)  # Default active status

        # Dictionaries to map names to IDs
        self.shop_profile_map = {}
        self.renter_profile_map = {}

        # UI Components
        self.create_form()

        # If editing an existing allocation, pre-fill the form
        if existing_allocation:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing allocation details."""
        # Populate dropdowns first
        self.populate_shop_profiles()
        self.populate_renter_profiles()

        # Find the display name for the shop and renter
        shop_display_name = None
        for name, shop_id in self.shop_profile_map.items():
            if shop_id == self.existing_allocation.shop_profile_id:
                shop_display_name = name
                break

        renter_display_name = None
        for name, renter_id in self.renter_profile_map.items():
            if renter_id == self.existing_allocation.renter_profile_id:
                renter_display_name = name
                break

        # Set the dropdowns and IDs
        if shop_display_name:
            self.shop_profile_dropdown.set(shop_display_name)
            self.shop_profile_id.set(self.existing_allocation.shop_profile_id)

        if renter_display_name:
            self.renter_profile_dropdown.set(renter_display_name)
            self.renter_profile_id.set(self.existing_allocation.renter_profile_id)

        # Set other fields
        self.from_year.set(str(self.existing_allocation.from_year))
        self.from_month.set(str(self.existing_allocation.from_month))
        self.to_year.set(str(self.existing_allocation.to_year))
        self.to_month.set(str(self.existing_allocation.to_month))
        self.close_status.set(self.existing_allocation.close_status)

    def create_form(self):
        """Creates the form for allocating a shop."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        # Shop Profile
        ttk.Label(form_frame, text="Shop:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.shop_profile_dropdown = ttk.Combobox(form_frame, textvariable=self.shop_profile_id, width=40)
        self.populate_shop_profiles()  # Populate the dropdown
        self.shop_profile_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # Renter Profile
        ttk.Label(form_frame, text="Renter:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.renter_profile_dropdown = ttk.Combobox(form_frame, textvariable=self.renter_profile_id, width=40)
        self.populate_renter_profiles()  # Populate the dropdown
        self.renter_profile_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # From Year
        ttk.Label(form_frame, text="From Year:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.from_year, width=40).grid(row=2, column=1, padx=5, pady=5)

        # From Month
        ttk.Label(form_frame, text="From Month:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.from_month, width=40).grid(row=3, column=1, padx=5, pady=5)

        # To Year
        ttk.Label(form_frame, text="To Year:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.to_year, width=40).grid(row=4, column=1, padx=5, pady=5)

        # To Month
        ttk.Label(form_frame, text="To Month:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.to_month, width=40).grid(row=5, column=1, padx=5, pady=5)

        # Close Status (Active/Closed)
        ttk.Label(form_frame, text="Close Status:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(form_frame, text="Close", variable=self.close_status, bootstyle="warning").grid(row=6, column=1, padx=5, pady=5)

        # Submit Button
        submit_text = "Save Allocation" if not self.existing_allocation else "Update Allocation"
        submit_command = self.save_shop_allocation
        self.submit_button = ttk.Button(
            self, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="success"
        )
        self.submit_button.pack(pady=(10, 0))

    def populate_shop_profiles(self):
        """Populate the shop profile dropdown with available shops from the database."""
        try:
            session = Session()
            shops = session.query(ShopProfile).all()
            
            # Clear existing map
            self.shop_profile_map.clear()
            
            # Create shop names and populate map
            shop_names = []
            for shop in shops:
                # Create a unique display name
                display_name = f"{shop.shop_name} (Floor: {shop.floor_no}, No: {shop.shop_no})"
                self.shop_profile_map[display_name] = shop.id
                shop_names.append(display_name)
            
            # Set dropdown values
            self.shop_profile_dropdown['values'] = shop_names
            
            # Set default selection to first shop if available
            if shop_names:
                self.shop_profile_dropdown.set(shop_names[0])
                self.shop_profile_id.set(self.shop_profile_map[shop_names[0]])
            
            # Bind selection event
            self.shop_profile_dropdown.bind("<<ComboboxSelected>>", self.on_shop_profile_select)

            session.close()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error fetching shop profiles: {str(e)}", title="Error", parent=self)

    def on_shop_profile_select(self, event):
        """Handles the selection of a shop profile from the dropdown."""
        selected_shop = self.shop_profile_dropdown.get()
        shop_id = self.shop_profile_map.get(selected_shop)
        if shop_id is not None:
            self.shop_profile_id.set(shop_id)
            print(f"Selected Shop ID: {shop_id}")

    def populate_renter_profiles(self):
        """Populate the renter profile dropdown with available renters from the database."""
        try:
            session = Session()
            renters = session.query(ShopRenterProfile).all()
            
            # Clear existing map
            self.renter_profile_map.clear()
            
            # Create renter names and populate map
            renter_names = []
            for renter in renters:
                # Create a unique display name
                display_name = f"{renter.renter_name} (Phone: {renter.phone})"
                self.renter_profile_map[display_name] = renter.id
                renter_names.append(display_name)
            
            # Set dropdown values
            self.renter_profile_dropdown['values'] = renter_names
            
            # Set default selection to first renter if available
            if renter_names:
                self.renter_profile_dropdown.set(renter_names[0])
                self.renter_profile_id.set(self.renter_profile_map[renter_names[0]])
            
            # Bind selection event
            self.renter_profile_dropdown.bind("<<ComboboxSelected>>", self.on_renter_profile_select)

            session.close()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error fetching renter profiles: {str(e)}", title="Error", parent=self)

    def on_renter_profile_select(self, event):
        """Handles the selection of a renter profile from the dropdown."""
        selected_renter = self.renter_profile_dropdown.get()
        renter_id = self.renter_profile_map.get(selected_renter)
        if renter_id is not None:
            self.renter_profile_id.set(renter_id)
            print(f"Selected Renter ID: {renter_id}")

    def save_shop_allocation(self):
        """Saves or updates the shop allocation to the database."""
        try:
            # Validate that selections have been made
            if not self.shop_profile_id.get():
                ttk.dialogs.Messagebox.show_warning(
                    message="Please select a shop profile.", 
                    title="Validation Error", 
                    parent=self
                )
                return

            if not self.renter_profile_id.get():
                ttk.dialogs.Messagebox.show_warning(
                    message="Please select a renter profile.", 
                    title="Validation Error", 
                    parent=self
                )
                return

            session = Session()

            if self.existing_allocation:
                # Update existing allocation
                allocation = session.query(ShopAllocation).filter_by(id=self.existing_allocation.id).first()
                if not allocation:
                    raise ValueError("Allocation not found")
                
                allocation.shop_profile_id = int(self.shop_profile_id.get())
                allocation.renter_profile_id = int(self.renter_profile_id.get())
                allocation.from_year = self.from_year.get()
                allocation.from_month = self.from_month.get()
                allocation.to_year = self.to_year.get()
                allocation.to_month = self.to_month.get()
                allocation.close_status = self.close_status.get()
                
                message = "Shop allocation updated successfully!"
            else:
                # Create new allocation
                new_allocation = ShopAllocation(
                    shop_profile_id=int(self.shop_profile_id.get()),
                    renter_profile_id=int(self.renter_profile_id.get()),
                    from_year=self.from_year.get(),
                    from_month=self.from_month.get(),
                    to_year=self.to_year.get(),
                    to_month=self.to_month.get(),
                    close_status=self.close_status.get()
                )
                session.add(new_allocation)
                message = "Shop allocation added successfully!"

            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(
                message=message, 
                title="Success", 
                parent=self
            )
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error saving shop allocation: {str(e)}", 
                title="Error", 
                parent=self
            )

    def clear_form(self):
        """Clear all form fields."""
        self.shop_profile_dropdown.set('')
        self.renter_profile_dropdown.set('')
        self.from_year.set('')
        self.from_month.set('')
        self.to_year.set('')
        self.to_month.set('')
        self.close_status.set(0)
