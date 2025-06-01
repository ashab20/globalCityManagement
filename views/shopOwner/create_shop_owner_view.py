import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, filedialog, messagebox
import base64
from sqlalchemy.orm import sessionmaker
from models.shop_owner_profile import ShopOwnerProfile
from utils.database import Session
import os

class CreateShopOwnerView(ttk.Frame):
    def __init__(self, parent, existing_shop_owner=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_shop_owner = existing_shop_owner

        # StringVars for input fields
        self.owner_name = StringVar()
        self.phone = StringVar()
        self.email = StringVar()
        self.address = StringVar()
        self.nid_number = StringVar()
        self.nid_front_base64 = StringVar()  # Store Base64 data
        self.nid_back_base64 = StringVar()

        # UI Components
        self.create_form()

        # If editing an existing shop owner, pre-fill the form
        if existing_shop_owner:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing shop owner details."""
        self.owner_name.set(self.existing_shop_owner.ownner_name)
        self.phone.set(self.existing_shop_owner.phone)
        self.email.set(self.existing_shop_owner.email)
        self.address.set(self.existing_shop_owner.address)
        self.nid_number.set(self.existing_shop_owner.nid_number)

        # Handle NID images
        if self.existing_shop_owner.nid_front:
            base64_front = base64.b64encode(self.existing_shop_owner.nid_front).decode('utf-8')
            self.nid_front_base64.set(base64_front)
            self.nid_front_label.config(text="NID Front Uploaded ✔", foreground="green")
        
        if self.existing_shop_owner.nid_back:
            base64_back = base64.b64encode(self.existing_shop_owner.nid_back).decode('utf-8')
            self.nid_back_base64.set(base64_back)
            self.nid_back_label.config(text="NID Back Uploaded ✔", foreground="green")

    def create_form(self):
        """Creates the form for entering shop owner details."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        # Owner Name
        ttk.Label(form_frame, text="Owner Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.owner_name, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Phone
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.phone, width=40).grid(row=1, column=1, padx=5, pady=5)

        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.email, width=40).grid(row=2, column=1, padx=5, pady=5)

        # Address
        ttk.Label(form_frame, text="Address:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.address, width=40).grid(row=3, column=1, padx=5, pady=5)

        # NID Number
        ttk.Label(form_frame, text="NID Number:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.nid_number, width=40).grid(row=4, column=1, padx=5, pady=5)

        # NID Front Upload
        ttk.Button(form_frame, text="Upload NID Front", command=self.upload_nid_front, bootstyle="info-outline").grid(row=5, column=0, padx=5, pady=5)
        self.nid_front_label = ttk.Label(form_frame, text="No file selected", foreground="gray")
        self.nid_front_label.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # NID Back Upload
        ttk.Button(form_frame, text="Upload NID Back", command=self.upload_nid_back, bootstyle="info-outline").grid(row=6, column=0, padx=5, pady=5)
        self.nid_back_label = ttk.Label(form_frame, text="No file selected", foreground="gray")
        self.nid_back_label.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Submit Button
        submit_text = "Save Shop Owner" if not self.existing_shop_owner else "Update Shop Owner"
        submit_command = self.save_shop_owner
        self.save_button = ttk.Button(
            self, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="success"
        )
        self.save_button.pack(pady=(10, 0))

    def upload_nid_front(self):
        """Upload front side of NID and convert to Base64."""
        file_path = filedialog.askopenfilename(
            title="Select NID Front",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]  # Corrected filetypes format
        )

        if file_path:
            try:
                with open(file_path, "rb") as file:
                    image_data = file.read()
                    base64_str = base64.b64encode(image_data).decode("utf-8")
                    self.nid_front_base64.set(base64_str)
                self.nid_front_label.config(text=f"File selected ✔ {os.path.basename(file_path)}", foreground="green")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image: {str(e)}")


    def upload_nid_back(self):
        """Upload back side of NID and convert to Base64."""
        file_path = filedialog.askopenfilename(
            title="Select NID Back",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]  # Corrected filetypes format
        )

        if file_path:
            try:
                with open(file_path, "rb") as file:
                    image_data = file.read()
                    base64_str = base64.b64encode(image_data).decode("utf-8")
                    self.nid_back_base64.set(base64_str)
                self.nid_back_label.config(text=f"File selected ✔ {os.path.basename(file_path)}", foreground="green")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image: {str(e)}")

    def save_shop_owner(self):
        """Saves or updates the shop owner in the database."""
        try:
            session = Session()
            
            # Decode Base64 strings to binary data
            nid_front_binary = base64.b64decode(self.nid_front_base64.get()) if self.nid_front_base64.get() else None
            nid_back_binary = base64.b64decode(self.nid_back_base64.get()) if self.nid_back_base64.get() else None
            
            if self.existing_shop_owner:
                # Update existing shop owner
                shop_owner = session.query(ShopOwnerProfile).filter_by(id=self.existing_shop_owner.id).first()
                if not shop_owner:
                    raise ValueError("Shop owner not found")
                
                shop_owner.ownner_name = self.owner_name.get()
                shop_owner.phone = self.phone.get()
                shop_owner.email = self.email.get()
                shop_owner.address = self.address.get()
                shop_owner.nid_number = self.nid_number.get()
                
                # Update NID images only if new ones are uploaded
                if nid_front_binary:
                    shop_owner.nid_front = nid_front_binary
                if nid_back_binary:
                    shop_owner.nid_back = nid_back_binary
                
                message = "Shop owner updated successfully!"
            else:
                # Create new shop owner
                new_owner = ShopOwnerProfile(
                    ownner_name=self.owner_name.get(),
                    phone=self.phone.get(),
                    email=self.email.get(),
                    address=self.address.get(),
                    nid_number=self.nid_number.get(),
                    nid_front=nid_front_binary,
                    nid_back=nid_back_binary,
                    active_status=1 
                )
                session.add(new_owner)
                message = "Shop owner added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving shop owner: {str(e)}", title="Error", parent=self)
            print(f"Error saving shop owner: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.owner_name.set("")
        self.phone.set("")
        self.email.set("")
        self.address.set("")
        self.nid_number.set("")
        self.nid_front_base64.set("")
        self.nid_back_base64.set("")
        self.nid_front_label.config(text="No file selected", foreground="gray")
        self.nid_back_label.config(text="No file selected", foreground="gray")
