import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from models.category import Category
from utils.database import Session

class CreateCategoryView(ttk.Frame):
    def __init__(self, parent, existing_category=None):
        super().__init__(parent)
        self.parent = parent
        self.existing_category = existing_category

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

        # If editing an existing utility setting, pre-fill the form
        if existing_category:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing utility setting details."""
        self.name.set(self.existing_category.name)
        self.description.set(self.existing_category.description)
        
        # Set the related head in combobox
        session = Session()
        category = session.query(Category).filter_by(id=self.existing_category.id).first()
        if category:
            self.name.set(category.name)
            self.description.set(category.description)
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
            text="Create/Update Category",
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
        ttk.Label(form_frame, text="Category Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.name, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Category Description:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.description, width=40).grid(row=1, column=1, padx=5, pady=5)




        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=20)

        # Submit Button
        submit_text = "Save Category" if not self.existing_category else "Update Category"
        self.save_button = ttk.Button(
            button_frame,
            text=submit_text,
            command=self.save_category,
            bootstyle="success",
            width=20
        )
        self.save_button.pack()

    def save_category(self):
        """Saves or updates the category in the database."""
        try:
            session = Session()
            
            if self.existing_category:
                # Update existing category
                category = session.query(Category).filter_by(id=self.existing_category.id).first()
                if not category:
                    raise ValueError("Category not found")
                
                category.name = self.name.get()
                category.description = self.description.get()
                
                message = "Category updated successfully!"
            else:
                # Create new category
                new_category = Category(
                    name=self.name.get(),
                    description=self.description.get()
                )
                session.add(new_category)
                message = "Category added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving category: {str(e)}", title="Error", parent=self)
            print(f"Error saving category: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.name.set("")
        self.description.set("")
