import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, filedialog
import base64
from sqlalchemy.orm import sessionmaker
from models.shop_owner_profile import ShopOwnerProfile
from utils.database import Session


class CreateShopOwnerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent

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

    def create_form(self):
        """Creates the form for entering shop owner details."""
        # ttk.Label(self, text="Create Shop Owner", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=(0, 20))

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

        # # NID Front Upload
        # ttk.Button(form_frame, text="Upload NID Front", command=self.upload_nid_front, bootstyle="info-outline").grid(row=5, column=0, padx=5, pady=5)
        # self.nid_front_label = ttk.Label(form_frame, text="No file selected", foreground="gray")
        # self.nid_front_label.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # # NID Back Upload
        # ttk.Button(form_frame, text="Upload NID Back", command=self.upload_nid_back, bootstyle="info-outline").grid(row=6, column=0, padx=5, pady=5)
        # self.nid_back_label = ttk.Label(form_frame, text="No file selected", foreground="gray")
        # self.nid_back_label.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Submit Button
        ttk.Button(self, text="Save Shop Owner", command=self.save_shop_owner, bootstyle="success").pack(pady=(10, 0))

    def upload_nid_front(self):
        """Upload front side of NID and convert to Base64."""
        file_path = filedialog.askopenfilename(title="Select NID Front", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            with open(file_path, "rb") as file:
                base64_str = base64.b64encode(file.read()).decode("utf-8")
                self.nid_front_base64.set(base64_str)
            self.nid_front_label.config(text="File selected ✔", foreground="green")

    def upload_nid_back(self):
        """Upload back side of NID and convert to Base64."""
        file_path = filedialog.askopenfilename(title="Select NID Back", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            with open(file_path, "rb") as file:
                base64_str = base64.b64encode(file.read()).decode("utf-8")
                self.nid_back_base64.set(base64_str)
            self.nid_back_label.config(text="File selected ✔", foreground="green")

    def save_shop_owner(self):
        """Saves the shop owner to the database."""
        try:
            session = Session()
            new_owner = ShopOwnerProfile(
                ownner_name=self.owner_name.get(),
                phone=self.phone.get(),
                email=self.email.get(),
                address=self.address.get(),
                nid_number=self.nid_number.get(),
                # nid_front=self.nid_front_base64.get(),
                # nid_back=self.nid_back_base64.get(),
                active_status=1  # Default to active
            )
            session.add(new_owner)
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message="Shop owner added successfully!", title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving shop owner: {str(e)}", title="Error", parent=self)

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
