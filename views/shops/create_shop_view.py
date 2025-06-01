import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_profile import ShopProfile
from models.shop_owner_profile import ShopOwnerProfile  # Assuming you have this model
from utils.database import Session
from ttkbootstrap.dialogs import Messagebox


class CreateShopView(ttk.Frame):
    def __init__(self, parent, existing_shop=None):
        super().__init__(parent)
        self.parent = parent
        self.existing_shop = existing_shop
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True)
        
        
        # Create form
        self.create_form()

    def _configure_canvas(self, event):
        # Update the width of the scrollable frame to fill the canvas
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
        # Get the required height for all content
        required_height = self.scrollable_frame.winfo_reqheight()
        
        # Configure the canvas's scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Set minimum size for the canvas
        self.canvas.configure(width=event.width, height=min(required_height, 600))  # Set max height to 600 pixels
    
    def bind_mouse_wheel(self):
        """Bind mouse wheel to scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel events
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _bound_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbound_to_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind enter/leave events
        self.scrollable_frame.bind("<Enter>", _bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", _unbound_to_mousewheel)
    
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

        # Create a container for the two columns
        columns_frame = ttk.Frame(form_frame)
        columns_frame.pack(fill="both", expand=True)

        # Create left and right columns
        left_column = ttk.Frame(columns_frame)
        right_column = ttk.Frame(columns_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right_column.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # Styling for labels and entries
        label_style = {"bootstyle": "primary", "font": ("Helvetica", 10)}
        entry_style = {"font": ("Helvetica", 10)}

        # Left Column Fields
        # Shop Name
        ttk.Label(left_column, text="Shop Name:", **label_style).pack(anchor="w")
        self.shop_name_entry = ttk.Entry(left_column, **entry_style)
        self.shop_name_entry.pack(fill="x", pady=(0, 10))

        # Floor No
        ttk.Label(left_column, text="Floor No:", **label_style).pack(anchor="w")
        self.floor_no_entry = ttk.Entry(left_column, **entry_style)
        self.floor_no_entry.pack(fill="x", pady=(0, 10))

        # Shop No
        ttk.Label(left_column, text="Shop No:", **label_style).pack(anchor="w")
        self.shop_no_entry = ttk.Entry(left_column, **entry_style)
        self.shop_no_entry.pack(fill="x", pady=(0, 10))

        # Description
        ttk.Label(left_column, text="Description:", **label_style).pack(anchor="w")
        self.description_entry = ttk.Entry(left_column, **entry_style)
        self.description_entry.pack(fill="x", pady=(0, 10))

        # Shop Size
        ttk.Label(left_column, text="Shop Size:", **label_style).pack(anchor="w")
        self.shop_size_entry = ttk.Entry(left_column, **entry_style)
        self.shop_size_entry.pack(fill="x", pady=(0, 10))


        # Right Column Fields
         # Internet Bill
        ttk.Label(right_column, text="Internet Bill:", **label_style).pack(anchor="w")
        self.internet_bill_entry = ttk.Entry(right_column, **entry_style)
        self.internet_bill_entry.pack(fill="x", pady=(0, 10))

        # Elect Demand Charge
        ttk.Label(right_column, text="Elect Demand Charge:", **label_style).pack(anchor="w")
        self.elect_demand_charge_entry = ttk.Entry(right_column, **entry_style)
        self.elect_demand_charge_entry.pack(fill="x", pady=(0, 10))

        # Rent Type
        ttk.Label(right_column, text="Rent Type:", **label_style).pack(anchor="w")
        self.rent_type_entry = ttk.Combobox(
            right_column, 
            values=["Contractual", "Per SFT"], 
            state="readonly",
            **entry_style
        )
        self.rent_type_entry.pack(fill="x", pady=(0, 10))
        
        # Create a frame for per square feet amount that can be shown/hidden
        self.per_sft_frame = ttk.Frame(right_column)
        self.per_sft_frame.pack(fill="x", pady=(0, 10))
        
        # Per Square Feet Amount (initially hidden)
        ttk.Label(self.per_sft_frame, text="Per SFT Amount:", **label_style).pack(anchor="w")
        self.per_sqr_fit_amt_entry = ttk.Entry(self.per_sft_frame, **entry_style)
        self.per_sqr_fit_amt_entry.pack(fill="x")
        
        # Initially hide the per square feet amount frame
        self.per_sft_frame.pack_forget()
        
        # Bind the rent type change event
        self.rent_type_entry.bind('<<ComboboxSelected>>', self._on_rent_type_change)

        # Rent Amount
        ttk.Label(right_column, text="Rent Amount:", **label_style).pack(anchor="w")
        self.rent_entry = ttk.Entry(right_column, **entry_style)
        self.rent_entry.pack(fill="x", pady=(0, 10))

        # Shop Owner
        ttk.Label(right_column, text="Shop Owner:", **label_style).pack(anchor="w")
        self.shop_owner_combobox = ttk.Combobox(
            right_column, 
            state="readonly",
            **entry_style
        )
        self.shop_owner_combobox.pack(fill="x", pady=(0, 10))

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
        self.save_button.pack(pady=(20, 0))

        # Create scrollable container
        self.canvas = ttk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Add form_frame to scrollable frame
        form_frame.pack_forget()  # Unpack from previous container
        form_frame.pack(in_=self.scrollable_frame, fill="both", expand=True)
        
        # Create window inside canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Configure canvas size
        self.canvas.bind('<Configure>', self._configure_canvas)
        
        # Bind mouse wheel
        self.bind_mouse_wheel()

        # Load shop owners into the combobox
        self.load_shop_owners()

        # Pre-fill data if editing an existing shop
        if self.existing_shop:
            self.shop_name_entry.insert(0, self.existing_shop.shop_name)
            self.floor_no_entry.insert(0, self.existing_shop.floor_no)
            self.shop_no_entry.insert(0, self.existing_shop.shop_no)
            self.description_entry.insert(0, self.existing_shop.descreption)
            self.shop_size_entry.insert(0, str(self.existing_shop.shop_size))
            self.elect_demand_charge_entry.insert(0, str(self.existing_shop.elect_demand_chrge))
            self.internet_bill_entry.insert(0, str(self.existing_shop.internet_bill))
            self.rent_type_entry.set(self.existing_shop.rent_type)
            self.rent_entry.insert(0, str(self.existing_shop.rent_amount))
    
    def _on_rent_type_change(self, event=None):
        """Handle rent type change event"""
        selected_type = self.rent_type_entry.get()
        if selected_type == "Per SFT":
            self.per_sft_frame.pack(fill="x", pady=(0, 10))
            # Calculate per SFT amount if rent and shop size are available
            try:
                rent = float(self.rent_entry.get()) if self.rent_entry.get() else 0
                shop_size = float(self.shop_size_entry.get()) if self.shop_size_entry.get() else 0
                if rent and shop_size:
                    per_sft = rent / shop_size
                    self.per_sqr_fit_amt_entry.delete(0, "end")
                    self.per_sqr_fit_amt_entry.insert(0, f"{per_sft:.2f}")
            except ValueError:
                pass
        else:
            self.per_sft_frame.pack_forget()
            self.per_sqr_fit_amt_entry.delete(0, "end")

    def create_shop(self):
        """Handle shop creation."""
        shop_name = self.shop_name_entry.get().strip()
        floor_no = self.floor_no_entry.get().strip()
        shop_no = self.shop_no_entry.get().strip()
        description = self.description_entry.get().strip()
        rent_amount = self.rent_entry.get().strip()
        internet_bill = self.internet_bill_entry.get().strip()
        rent_type = self.rent_type_entry.get().strip()
        shop_size = self.shop_size_entry.get().strip()

        shop_owner_name = self.shop_owner_combobox.get().strip()

        elect_demand_charge = self.elect_demand_charge_entry.get().strip()

        if not all([shop_name, floor_no, shop_no, description, shop_owner_name, elect_demand_charge]):
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
        per_sqr_fit_amt = 0
        if rent_type == "Per Square Feet":
            per_sqr_fit_amt = rent / shop_size
        elif rent_type == "Fixed":
            per_sqr_fit_amt = 0 

        try:
            # Retrieve the shop owner id based on the selected owner name
            session = Session()
            shop_owner = session.query(ShopOwnerProfile).filter_by(ownner_name=shop_owner_name).first()  
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
                self.existing_shop.elect_demand_chrge = elect_demand_charge
                self.existing_shop.rent_amount = rent
                self.existing_shop.internet_bill = internet_bill
                self.existing_shop.shop_owner_id = shop_owner.id
                session.add(self.existing_shop)
            else:
                # Create new shop profile
                new_shop = ShopProfile(
                    shop_owner_id=shop_owner.id,
                    floor_no=floor_no,
                    shop_no=shop_no,
                    shop_name=shop_name,
                    descreption=description,
                    rent_type=rent_type,
                    shop_size=shop_size,
                    per_sqr_fit_amt=per_sqr_fit_amt,
                    rent_amount=rent,
                    elect_demand_chrge=elect_demand_charge,
                    internet_bill=internet_bill,
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
            self.elect_demand_charge_entry.delete(0, "end")
            self.internet_bill_entry.delete(0, "end")
            self.rent_type_entry.delete(0, "end")
            self.shop_owner_combobox.set('')

        except Exception as e:
            Messagebox.show_error(message=f"Error creating shop: {str(e)}", title="Error", parent=self)
