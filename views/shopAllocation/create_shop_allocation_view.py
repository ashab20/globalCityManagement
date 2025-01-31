import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, IntVar
from sqlalchemy.orm import sessionmaker
from models.shop_allocation import ShopAllocation
from models.shop_profile import ShopProfile
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session


class CreateShopAllocationView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent

        # StringVars for input fields
        self.shop_profile_id = StringVar()
        self.renter_profile_id = StringVar()
        self.from_year = StringVar()
        self.from_month = StringVar()
        self.to_year = StringVar()
        self.to_month = StringVar()
        self.close_status = IntVar(value=0)  # Default active status

        # UI Components
        self.create_form()

    def create_form(self):
        """Creates the form for allocating a shop."""
        # ttk.Label(self, text="Create Shop Allocation", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=(0, 20))

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
        ttk.Button(self, text="Save Allocation", command=self.save_shop_allocation, bootstyle="success").pack(pady=(10, 0))

    def populate_shop_profiles(self):
        """Populate the shop profile dropdown with available shops from the database."""
        try:
            session = Session()
            shops = session.query(ShopProfile).all()
            # Create a list of tuples with (id, formatted_name) for easier use later
            shop_names = [(shop.id, f"{shop.id} - {shop.shop_name}") for shop in shops]
            # Set the dropdown values to the formatted names
            self.shop_profile_dropdown['values'] = [shop_name[1] for shop_name in shop_names]
            
            # Store the ID value of the selected shop for later use
            self.shop_profile_dropdown.bind("<<ComboboxSelected>>", self.on_shop_profile_select)

            session.close()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error fetching shop profiles: {str(e)}", title="Error", parent=self)

    def on_shop_profile_select(self, event):
        """Handles the selection of a shop profile from the dropdown."""
        selected_shop = self.shop_profile_dropdown.get()
        shop_id = int(selected_shop.split(" - ")[0])
        self.shop_profile_id.set(shop_id)
        print(f"Selected Shop ID: {shop_id}")

    def populate_renter_profiles(self):
        """Populate the renter profile dropdown with available renters from the database."""
        try:
            session = Session()
            renters = session.query(ShopRenterProfile).all()
            renter_names = [(renter.id, f"{renter.id} - {renter.renter_name}") for renter in renters]
            # Set the dropdown values to the formatted names
            self.renter_profile_dropdown['values'] = [renter_name[1] for renter_name in renter_names]
            
            # Store the ID value of the selected renter for later use
            self.renter_profile_dropdown.bind("<<ComboboxSelected>>", self.on_renter_profile_select)

            session.close()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error fetching renter profiles: {str(e)}", title="Error", parent=self)



    def on_renter_profile_select(self, event):
        """Handles the selection of a renter profile from the dropdown."""
        selected_renter = self.renter_profile_dropdown.get()
        renter_id = int(selected_renter.split(" - ")[0])  # Extract ID from the selection
        self.renter_profile_id.set(renter_id)  # Store the ID for later use
        print(f"Selected Renter ID: {renter_id}")


    def save_shop_allocation(self):
            """Saves the shop allocation to the database."""
            try:
                session = Session()

                new_allocation = ShopAllocation(
                    shop_profile_id=self.shop_profile_id.get(),
                    renter_profile_id=self.renter_profile_id.get(),
                    from_year=self.from_year.get(),
                    from_month=self.from_month.get(),
                    to_year=self.to_year.get(),
                    to_month=self.to_month.get(),
                    close_status=self.close_status.get()
                )

                session.add(new_allocation)
                session.commit()
                session.close()

                ttk.dialogs.Messagebox.show_info(message="Shop allocation added successfully!", title="Success", parent=self)
                self.clear_form()
            except Exception as e:
                ttk.dialogs.Messagebox.show_error(message=f"Error saving shop allocation: {str(e)}", title="Error", parent=self)

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.shop_profile_id.set("")
        self.renter_profile_id.set("")
        self.from_year.set("")
        self.from_month.set("")
        self.to_year.set("")
        self.to_month.set("")
        self.close_status.set(0)
