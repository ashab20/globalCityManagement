import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, filedialog, messagebox
import base64
from sqlalchemy.orm import sessionmaker
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session
import threading
import os

from utils.image_uploader import file_to_base64

class CreateShopRenterView(ttk.Frame):
    def __init__(self, parent, existing_renter=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_renter = existing_renter

        # StringVars for input fields
        self.renter_name = StringVar()
        self.phone = StringVar()
        self.email = StringVar()
        self.address = StringVar()
        self.nid_number = StringVar()
        self.nid_front_base64 = StringVar() 
        self.nid_back_base64 = StringVar()
        self.documents_base64 = StringVar()

        # UI Components
        self.create_form()

        # If editing an existing renter, pre-fill the form
        if existing_renter:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing renter details."""
        self.renter_name.set(self.existing_renter.renter_name)
        self.phone.set(self.existing_renter.phone)
        self.email.set(self.existing_renter.email)
        self.address.set(self.existing_renter.address)
        self.nid_number.set(self.existing_renter.nid_number)

    def create_form(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        # Renter Name
        ttk.Label(form_frame, text="Renter Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.renter_name, width=40).grid(row=0, column=1, padx=5, pady=5)

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

        # Documents Upload
        ttk.Button(form_frame, text="Upload Documents", command=self.upload_documents, bootstyle="info-outline").grid(row=7, column=0, padx=5, pady=5)
        self.documents_label = ttk.Label(form_frame, text="No file selected", foreground="gray")
        self.documents_label.grid(row=7, column=1, sticky="w", padx=5, pady=5)

        # Submit Button
        submit_text = "Save Shop Renter" if not self.existing_renter else "Update Shop Renter"
        submit_command = self.save_shop_renter
        self.submit_button = ttk.Button(self, text=submit_text, command=submit_command, bootstyle="success")
        self.submit_button.pack(pady=(10, 0))

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

    def upload_documents(self):
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
                    self.documents_base64.set(base64_str)
                self.documents_label.config(text=f"File selected ✔ {os.path.basename(file_path)}", foreground="green")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read image: {str(e)}")

    # def upload_documents(self):
    #     """Upload and process additional documents."""
    #     try:
    #         file_path = filedialog.askopenfilename(
    #             title="Select Document",
    #             filetypes=[("PDF Files", "*.pdf"), ("Image Files", "*.png;*.jpg;*.jpeg")]
    #         )
    #         if not file_path:
    #             print("No file selected.")
    #             return

    #         is_image = file_path.lower().endswith((".png", ".jpg", ".jpeg"))
    #         base64_str = file_to_base64(file_path, is_image=is_image)

    #         if base64_str:
    #             self.documents_base64.set(base64_str)
    #             self.documents_label.config(
    #                 text=f"File selected ✔ {os.path.basename(file_path)}", foreground="green"
    #             )
    #         else:
    #             self.documents_label.config(text="Error processing file", foreground="red")
    #     except Exception as e:
    #         print(f"Error uploading document: {str(e)}")
    #         messagebox.showerror("Error", f"Error uploading file: {str(e)}")
    #         self.documents_label.config(text="Error uploading file", foreground="red")
    
    def save_shop_renter(self):
        """Saves or updates the shop renter in the database."""
        try:
            session = Session()
            
            if self.existing_renter:
                # Update existing renter
                renter = session.query(ShopRenterProfile).filter_by(id=self.existing_renter.id).first()
                if not renter:
                    raise ValueError("Renter not found")
                
                renter.renter_name = self.renter_name.get()
                renter.phone = self.phone.get()
                renter.email = self.email.get()
                renter.address = self.address.get()
                renter.nid_number = self.nid_number.get()
                
                message = "Shop renter updated successfully!"
            else:
                # Create new renter
                new_renter = ShopRenterProfile(
                    renter_name=self.renter_name.get(),
                    phone=self.phone.get(),
                    email=self.email.get(),
                    address=self.address.get(),
                    nid_number=self.nid_number.get(),
                    active_status=1  # Default to active
                )
                session.add(new_renter)
                message = "Shop renter added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving shop renter: {str(e)}", title="Error", parent=self)
            print(f"Error saving shop renter: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.renter_name.set("")
        self.phone.set("")
        self.email.set("")
        self.address.set("")
        self.nid_number.set("")
        self.nid_front_base64.set("")
        self.nid_back_base64.set("")
        self.documents_base64.set("")
        self.nid_front_label.config(text="No file selected", foreground="gray")
        self.nid_back_label.config(text="No file selected", foreground="gray")
        self.documents_label.config(text="No file selected", foreground="gray")
