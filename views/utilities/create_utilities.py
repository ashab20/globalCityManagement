import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from sqlalchemy.orm import sessionmaker
from models.UtilitySetting import UtilitySetting
from utils.database import Session
from datetime import datetime
from models.acc_head_of_accounts import AccHeadOfAccounts

class CreateUtilitySettingView(ttk.Frame):
    def __init__(self, parent, existing_utility=None):
        super().__init__(parent)
        self.parent = parent
        self.existing_utility = existing_utility

        # Configure grid weights for centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)

        # StringVars for input fields
        self.utility_name = StringVar()
        self.utility_unit = StringVar()
        self.utility_rate = StringVar()
        self.releted_head_id = StringVar()
        self.releted_head_display = StringVar()
        self.remarks = StringVar()
        
        # Dictionary to store head information
        self.heads_dict = {}

        # UI Components
        self.create_form()
        
        # Load related heads
        self.load_releted_head()

        # If editing an existing utility setting, pre-fill the form
        if existing_utility:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing utility setting details."""
        self.utility_name.set(self.existing_utility.utility_name)
        self.utility_unit.set(self.existing_utility.utility_unit)
        self.utility_rate.set(str(self.existing_utility.utility_rate))
        self.remarks.set(self.existing_utility.remarks)
        
        # Set the related head in combobox
        session = Session()
        head = session.query(AccHeadOfAccounts).filter_by(id=self.existing_utility.releted_head_id).first()
        if head:
            head_display = f"{head.head_name}"
            self.releted_head_display.set(head_display)
            self.releted_head_id.set(str(head.id))
        session.close()

    def create_form(self):
        """Creates the form for entering utility setting details."""
        # Create main container for centering
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0)

        # Create title frame
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            title_frame,
            text="Create/Update Utility",
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

        # Utility Name
        ttk.Label(form_frame, text="Utility Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.utility_name, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Utility Unit:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.unit_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.utility_unit,
            values=["PCS", "KG", "LITRE", "METER", "UNIT", "KW", "%", "Month", "YEAR"],
            state="readonly",
            width=37
        )
        self.unit_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Utility Rate
        ttk.Label(form_frame, text="Utility Rate:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.utility_rate, width=40).grid(row=2, column=1, padx=5, pady=5)

        # Remarks
        ttk.Label(form_frame, text="Remarks:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.remarks, width=40).grid(row=3, column=1, padx=5, pady=5)

        # Related Head combobox
        ttk.Label(form_frame, text="Related Head:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.releted_head_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.releted_head_display,
            width=40,
            state="readonly"
        )
        self.releted_head_combobox.grid(row=4, column=1, padx=5, pady=5)
        self.releted_head_combobox.bind("<<ComboboxSelected>>", self.on_releted_head_selected)

        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=20)

        # Submit Button
        submit_text = "Save Utility" if not self.existing_utility else "Update Utility"
        self.save_button = ttk.Button(
            button_frame,
            text=submit_text,
            command=self.save_utility,
            bootstyle="success",
            width=20
        )
        self.save_button.pack()

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
                utility.utility_unit = self.utility_unit.get()
                utility.utility_rate = float(self.utility_rate.get())
                utility.releted_head_id = int(self.releted_head_id.get())
                utility.remarks = self.remarks.get()
                
                message = "Utility setting updated successfully!"
            else:
                # Create new utility setting
                new_utility = UtilitySetting(
                    utility_name=self.utility_name.get(),
                    utility_unit=self.utility_unit.get(),
                    utility_rate=float(self.utility_rate.get()),
                    releted_head_id=int(self.releted_head_id.get()),
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

    def on_releted_head_selected(self, event):
        """Handle related head selection"""
        selected = self.releted_head_combobox.get()
        if selected:
            # Get the head ID from our dictionary
            head_id = self.heads_dict.get(selected)
            if head_id:
                self.releted_head_id.set(str(head_id))

    def load_releted_head(self):
        """Load the related heads from the database"""
        try:
            session = Session()
            # Get all heads where head_lvl4th_id is 9
            heads = session.query(AccHeadOfAccounts).filter_by(head_lvl4th_id=9).all()
            
            # Clear existing items
            self.heads_dict.clear()
            
            # Create display items and populate dictionary
            head_items = []
            for head in heads:
                display_text = f"{head.head_name}"  # Only show the name
                head_items.append(display_text)
                self.heads_dict[display_text] = head.id
            
            # Update combobox values
            self.releted_head_combobox['values'] = head_items
            
            session.close()
            
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading related heads: {str(e)}", 
                title="Error", 
                parent=self
            )

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.utility_name.set("")
        self.utility_unit.set("")
        self.utility_rate.set("")
        self.releted_head_id.set("")
        self.releted_head_display.set("")  # Clear the display text
        self.remarks.set("")
