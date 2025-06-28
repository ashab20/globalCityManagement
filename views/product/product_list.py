from models.product import Product
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.category import Category
from models.unit import Unit
from utils.database import Session
from views.category.create_category import CreateCategoryView
from views.product.create_product import CreateProductView


class ProductListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Create product list
        self.create_product_list()

    def create_product_list(self):
        """Creates the product list view."""
        columns = ("ID", "Name", "Description", "Category", "Unit", "Status", "Edit", "Delete")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Unit", text="Unit")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("Description", width=200, anchor="w")
        self.tree.column("Category", width=100, anchor="w")
        self.tree.column("Unit", width=80, anchor="center")
        self.tree.column("Status", width=80, anchor="center")
        self.tree.column("Edit", width=75, anchor="center")
        self.tree.column("Delete", width=75, anchor="center")

        # Add vertical scrollbar
        yscrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=yscrollbar.set)

        # Add horizontal scrollbar
        xscrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview,
            bootstyle="primary-round"
        )
        self.tree.configure(xscrollcommand=xscrollbar.set)

        # Pack widgets
        self.tree.pack(side="top", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar.pack(side="bottom", fill="x")

        # Load products
        self.load_products()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_products,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)

    def load_products(self):
        """Load products from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            # Join with Category and Unit to get names
            products = session.query(Product, Category.name.label('category_name'), Unit.unit_name.label('unit_name')).join(
                Category, Product.category_id == Category.id, isouter=True
            ).join(
                Unit, Product.unit_id == Unit.id, isouter=True
            ).all()

            for product, category_name, unit_name in products:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        product.id,
                        product.name,
                        product.description or "",
                        category_name or "No Category",
                        unit_name or "No Unit",
                        "Active" if product.status == 1 else "Inactive",
                        "Edit",
                        "Delete"
                    ),
                    tags=(product.id,)
                )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading products: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            product_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 8:  # Delete column
                self.delete_product(product_id)
            elif col_num == 7:  # Edit column
                self.edit_product(product_id)

    def edit_product(self, product_id):
        """Edit product details."""
        session = Session()
        product = session.query(Product).filter_by(id=product_id).first()
        session.close()

        if product:
            # Create edit window
            edit_window = ttk.Toplevel(self)
            edit_window.title(f"Edit Product - {product.name}")
            edit_window.geometry("600x400")
            
            edit_view = CreateProductView(edit_window, existing_product=product)
            edit_view.pack(fill="both", expand=True)
            
            # Update save button to refresh list
            edit_view.save_button.configure(
                command=lambda: [
                    edit_view.save_product(),
                    edit_window.destroy(),
                    self.load_products()
                ]
            )

    def delete_product(self, product_id):
        """Delete product by ID with confirmation."""
        try:
            session = Session()
            product_to_delete = session.query(Product).filter_by(id=product_id).first()

            if product_to_delete:
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete product '{product_to_delete.name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(product_to_delete)
                    session.commit()
                    self.load_products()

                    Messagebox.show_info(
                        message="Product deleted successfully!",
                        title="Success",
                        parent=self
                    )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting product: {str(e)}",
                title="Error",
                parent=self
            )
