import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from models.particular import Particular
from utils.database import Session
from datetime import datetime

class CreateParticularView(ttk.Frame):
    def __init__(self, parent, existing_particular=None):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.existing_particular = existing_particular

        # StringVars for input fields
        self.particular_name = StringVar()
        self.particular_unit = StringVar()

        # UI Components
        self.create_form()

        # If editing an existing utility setting, pre-fill the form
        if existing_particular:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing utility setting details."""
        self.particular_name.set(self.existing_particular.name)
        self.particular_unit.set(self.existing_particular.unit)

    def create_form(self):
        """Creates the form for entering particular details."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=10)

        # Utility Name
        ttk.Label(form_frame, text="Particular Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.particular_name, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Utility Unit
        ttk.Label(form_frame, text="Particular Unit:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.particular_unit, width=40).grid(row=1, column=1, padx=5, pady=5)

        
        # Submit Button
        submit_text = "Save Particular" if not self.existing_particular else "Update Particular"
        submit_command = self.save_particular
        self.save_button = ttk.Button(
            self, 
            text=submit_text, 
            command=submit_command, 
            bootstyle="success"
        )
        self.save_button.pack(pady=(10, 0))

    def save_particular(self):
        """Saves or updates the utility setting in the database."""
        try:
            session = Session()
            
            if self.existing_particular:
                # Update existing utility setting
                particular = session.query(Particular).filter_by(id=self.existing_particular.id).first()
                if not particular:
                    raise ValueError("Particular not found")
                
                particular.name = self.particular_name.get()
                particular.unit = self.particular_unit.get()
                
                message = "Particular updated successfully!"
            else:
                # Create new utility setting
                new_particular = Particular(
                    name=self.particular_name.get(),
                    unit=self.particular_unit.get()
                )
                session.add(new_particular)
                message = "Particular added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving particular: {str(e)}", title="Error", parent=self)
            print(f"Error saving particular: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.particular_name.set("")
        self.particular_unit.set("")
