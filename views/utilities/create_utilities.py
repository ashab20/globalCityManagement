import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from sqlalchemy.orm import sessionmaker
from models.UtilitySetting import UtilitySetting
from utils.database import Session
from datetime import datetime

class CreateUtilitySettingView(ttk.Frame):
    def __init__(self, parent, existing_utility=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_utility = existing_utility

        # StringVars for input fields
        self.utility_name = StringVar()
        self.utility_rate = StringVar()
        self.remarks = StringVar()

        # UI Components
        self.create_form()

        # If editing an existing utility setting, pre-fill the form
        if existing_utility:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing utility setting details."""
        self.utility_name.set(self.existing_utility.utility_name)
        self.utility_rate.set(str(self.existing_utility.utility_rate))
        self.remarks.set(self.existing_utility.remarks)

    def create_form(self):
        """Creates the form for entering utility setting details."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        # Utility Name
        ttk.Label(form_frame, text="Utility Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.utility_name, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Utility Rate
        ttk.Label(form_frame, text="Utility Rate:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.utility_rate, width=40).grid(row=1, column=1, padx=5, pady=5)

        # Remarks
        ttk.Label(form_frame, text="Remarks:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.remarks, width=40).grid(row=2, column=1, padx=5, pady=5)

        # Submit Button
        submit_text = "Save Utility" if not self.existing_utility else "Update Utility"
        submit_command = self.save_utility
        self.save_button = ttk.Button(
            self, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="success"
        )
        self.save_button.pack(pady=(10, 0))

    def save_utility(self):
        """Saves or updates the utility setting in the database."""
        try:
            session = Session()
            
            if self.existing_utility:
                # Update existing utility setting
                utility = session.query(UtilitySetting).filter_by(id=self.existing_utility.id).first()
                if not utility:
                    raise ValueError("Utility setting not found")
                
                utility.utility_name = self.utility_name.get()
                utility.utility_rate = float(self.utility_rate.get())
                utility.remarks = self.remarks.get()
                
                message = "Utility setting updated successfully!"
            else:
                # Create new utility setting
                new_utility = UtilitySetting(
                    utility_name=self.utility_name.get(),
                    utility_rate=float(self.utility_rate.get()),
                    remarks=self.remarks.get()
                )
                session.add(new_utility)
                message = "Utility setting added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving utility setting: {str(e)}", title="Error", parent=self)
            print(f"Error saving utility setting: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.utility_name.set("")
        self.utility_rate.set("")
        self.remarks.set("")
