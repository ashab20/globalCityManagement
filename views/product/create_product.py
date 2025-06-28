from models.category import Category
from models.product import Product
from models.unit import Unit
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
from utils.database import Session

class CreateProductView(ttk.Frame):
    def __init__(self, parent, existing_product=None):
        super().__init__(parent)
        self.parent = parent
        self.existing_product = existing_product

        # Configure grid weights for centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)

        # StringVars for input fields
        self.product_name = StringVar()
        self.product_description = StringVar()
        self.product_category_id = StringVar()
        self.product_unit_id = StringVar()
        self.product_status = StringVar()
        self.selected_category_name = StringVar()  # For displaying category name
        self.selected_unit_name = StringVar()      # For displaying unit name
        self.category_list = []

        # UI Components
        self.create_form()

        # If editing an existing product, pre-fill the form
        if existing_product:
            self.pre_fill_form()

    def pre_fill_form(self):
        """Pre-fill form with existing product details."""
        self.product_name.set(self.existing_product.name)
        self.product_description.set(self.existing_product.description or "")
        self.product_status.set("Active" if self.existing_product.status == 1 else "Deactive")
        
        # Set the category and unit in combobox
        session = Session()
        product = session.query(Product).filter_by(id=self.existing_product.id).first()
        if product:
            self.product_name.set(product.name)
            self.product_description.set(product.description or "")
            self.product_status.set("Active" if product.status == 1 else "Deactive")
            
            # Set category name in combobox
            if product.category_id:
                category = session.query(Category).filter_by(id=product.category_id).first()
                if category:
                    self.selected_category_name.set(category.name)
                    self.product_category_id.set(str(category.id))
            
            # Set unit name in combobox
            if product.unit_id:
                unit = session.query(Unit).filter_by(id=product.unit_id).first()
                if unit:
                    self.selected_unit_name.set(unit.unit_name)
                    self.product_unit_id.set(str(unit.id))
        session.close()

    def create_form(self):
        """Creates the form for entering product details."""
        # Create main container for centering
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0)

        # Create title frame
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            title_frame,
            text="Create/Update Product",
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

        # Product Name
        ttk.Label(form_frame, text="Product Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.product_name, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Product Description
        ttk.Label(form_frame, text="Product Description:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.product_description, width=40).grid(row=1, column=1, padx=5, pady=5)

        # Product Category
        ttk.Label(form_frame, text="Product Category:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.product_category_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.selected_category_name,  # show name
            width=40,
            state="readonly"
        )
        self.product_category_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.product_category_combobox.bind("<<ComboboxSelected>>", self.on_category_selected)
        self.load_categories()

        # Product Unit
        ttk.Label(form_frame, text="Product Unit:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.product_unit_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.selected_unit_name,  # show name
            width=40,
            state="readonly"
        )
        self.product_unit_combobox.grid(row=3, column=1, padx=5, pady=5)
        self.product_unit_combobox.bind("<<ComboboxSelected>>", self.on_unit_selected)
        self.load_units()

        # Product Status
        ttk.Label(form_frame, text="Product Status:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.product_status_combobox = ttk.Combobox(form_frame, textvariable=self.product_status, width=40, state="readonly")
        self.product_status_combobox.grid(row=4, column=1, padx=5, pady=5)
        self.product_status_combobox['values'] = ["Active", "Deactive"]
        self.product_status.set("Active")  # Default to Active

        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=20)

        # Submit Button
        submit_text = "Save Product" if not self.existing_product else "Update Product"
        self.save_button = ttk.Button(
            button_frame,
            text=submit_text,
            command=self.save_product,
            bootstyle="success",
            width=20
        )
        self.save_button.pack()

    def load_categories(self):
        try:
            session = Session()
            categories = session.query(Category).filter_by(status=1).all()
            print('categories',categories)
            
            category_options = [(str(cat.id), cat.name) for cat in categories]
            category_names = [cat.name for cat in categories]  # <- name list for dropdown
            
            self.product_category_combobox['values'] = category_names
            self.category_mapping = {cat.name: str(cat.id) for cat in categories}  # name -> id
            session.close()
        except Exception as e:
            print(f"Error loading categories: {str(e)}")
            ttk.dialogs.Messagebox.show_error(message=f"Error loading categories: {str(e)}", title="Error", parent=self)

    def load_units(self):
        try:
            session = Session()
            units = session.query(Unit).filter_by(status=1).all()
            print('units',units)
            
            unit_names = [unit.unit_name for unit in units]
            self.product_unit_combobox['values'] = unit_names
            self.unit_mapping = {unit.unit_name: str(unit.id) for unit in units}  # name -> id
            session.close()
        except Exception as e:
            print(f"Error loading units: {str(e)}")
            ttk.dialogs.Messagebox.show_error(message=f"Error loading units: {str(e)}", title="Error", parent=self)

    def on_category_selected(self, event):
        selected = self.product_category_combobox.get()
        if selected in self.category_mapping:
            self.product_category_id.set(self.category_mapping[selected])

    def on_unit_selected(self, event):
        selected = self.product_unit_combobox.get()
        if selected in self.unit_mapping:
            self.product_unit_id.set(self.unit_mapping[selected])

    def check_product_name_exists(self, product_name, exclude_id=None):
        """Check if a product name already exists in the database."""
        try:
            session = Session()
            query = session.query(Product).filter(Product.name == product_name)
            
            # Exclude current product when editing
            if exclude_id:
                query = query.filter(Product.id != exclude_id)
            
            existing_product = query.first()
            session.close()
            
            return existing_product is not None
        except Exception as e:
            print(f"Error checking product name: {str(e)}")
            return False

    def get_category_list(self):
        """Get category list from the database."""
        session = Session()
        categories = session.query(Category).all()
        session.close()
        return categories

    def save_product(self):
        """Saves or updates the product in the database."""
        try:
            # Validate product name
            product_name = self.product_name.get().strip()
            if not product_name:
                ttk.dialogs.Messagebox.show_error(message="Product name is required!", title="Validation Error", parent=self)
                return
            
            # Check for duplicate product name
            exclude_id = self.existing_product.id if self.existing_product else None
            if self.check_product_name_exists(product_name, exclude_id):
                ttk.dialogs.Messagebox.show_warning(
                    message=f"Product '{product_name}' already exists. Please use a different product name.",
                    title="Duplicate Product",
                    parent=self
                )
                return
            
            session = Session()
            
            # Get category ID from the selected value
            category_id = None
            if self.product_category_id.get():
                try:
                    category_id = int(self.product_category_id.get())
                except ValueError:
                    # If it's not a direct ID, try to extract from the combobox selection
                    selected = self.product_category_combobox.get()
                    if selected in self.category_mapping:
                        category_id = int(self.category_mapping[selected])
            
            # Get unit ID from the selected value
            unit_id = None
            if self.product_unit_id.get():
                try:
                    unit_id = int(self.product_unit_id.get())
                except ValueError:
                    # If it's not a direct ID, try to extract from the combobox selection
                    selected = self.product_unit_combobox.get()
                    if selected in self.unit_mapping:
                        unit_id = int(self.unit_mapping[selected])
            
            # Get status value
            status = 1 if self.product_status.get() == "Active" else 0
            
            if self.existing_product:
                # Update existing product
                product = session.query(Product).filter_by(id=self.existing_product.id).first()
                if not product:
                    raise ValueError("Product not found")
                
                product.name = product_name
                product.description = self.product_description.get().strip()
                product.category_id = category_id
                product.unit_id = unit_id
                product.status = status
                
                message = "Product updated successfully!"
            else:
                # Create new product
                new_product = Product(
                    name=product_name,
                    description=self.product_description.get().strip(),
                    category_id=category_id,
                    unit_id=unit_id,
                    status=status
                )
                session.add(new_product)
                message = "Product added successfully!"
            
            session.commit()
            session.close()

            ttk.dialogs.Messagebox.show_info(message=message, title="Success", parent=self)
            self.clear_form()
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error saving product: {str(e)}", title="Error", parent=self)
            print(f"Error saving product: {str(e)}")

    def clear_form(self):
        """Clears the form fields after successful submission."""
        self.product_name.set("")
        self.product_description.set("")
        self.product_category_id.set("")
        self.product_unit_id.set("")
        self.selected_category_name.set("")
        self.selected_unit_name.set("")
        self.product_status.set("Active")
