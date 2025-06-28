import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from models.unit import Unit
from utils.database import Session

class CreateUnitView(ttk.Frame):
    def __init__(self, parent, existing_unit=None):
        super().__init__(parent)
        self.parent = parent
        self.existing_unit = existing_unit

        # Configure grid weights for centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)

        # StringVars for input fields
        self.name = StringVar()
        self.description = StringVar()
        
        # Dictionary to store head information
        self.heads_dict = {}

        # UI Components
        self.create_form()

        # If editing an existing unit, pre-fill the form
        if existing_unit:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing unit details."""
        self.name.set(self.existing_unit.unit_name)
        
        # Set the unit name
        session = Session()
        unit = session.query(Unit).filter_by(id=self.existing_unit.id).first()
        if unit:
            self.name.set(unit.unit_name)
        session.close()

    def create_form(self):
        """Creates the form for entering unit details."""
        # Create main container for centering
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0)

        # Create title frame
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            title_frame,
            text="Create/Update Unit",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        title_label.pack(anchor="center")

        # Create form frame with padding and border
        form_frame = ttk.Frame(main_container, padding=20)
        form_frame.pack()

        # Add a subtle border around the form
        style = ttk.Style()
        style.configure('Form.TFrame', borderwidth=1, relief='solid')
        form_frame['style'] = 'Form.TFrame'

        # Unit Name
        ttk.Label(form_frame, text="Unit Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.name, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=20)

        # Submit Button
        submit_text = "Save Unit" if not self.existing_unit else "Update Unit"
        self.save_button = ttk.Button(
            button_frame,
            text=submit_text,
            command=self.save_unit,
            bootstyle="success",
            width=20
        )
        self.save_button.pack()

    def save_unit(self):
        """Saves or updates the unit in the database."""
        try:
            session = Session()
            
            if self.existing_unit:
                # Update existing unit
                unit = session.query(Unit).filter_by(id=self.existing_unit.id).first()
                if not unit:
                    raise ValueError("Unit not found")
                
                unit.unit_name = self.name.get()
              
                message = "Unit updated successfully!"
            else:

                check_unit = session.query(Unit).filter_by(unit_name=self.name.get()).first()
                if check_unit:
                    ttk.dialogs.Messagebox.show_error(message="Unit already exists", title="Error", parent=self)
                    return
                
                # Create new unit
                new_unit = Unit(
                    unit_name=self.name.get()
                )
                session.add(new_unit)
                message = "Unit added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving unit: {str(e)}", title="Error", parent=self)
            print(f"Error saving unit: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.name.set("")
        self.description.set("")
