import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.category import Category
from utils.database import Session
from views.category.create_category import CreateCategoryView


class CategoryListView(ttk.Frame):
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

        # Create category list
        self.create_category_list()

    def create_category_list(self):
        """Creates the category list view."""
        columns = ("ID", "Name", "Description", "Status", "Edit", "Delete")
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
        self.tree.heading("Status", text="Status")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=100, anchor="w")
        self.tree.column("Description", width=100, anchor="w")
        self.tree.column("Status", width=100, anchor="center")
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

        # Load categories
        self.load_categories()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_categories,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)

    def load_categories(self):
        """Load categories from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            categories = session.query(Category).all()

            for category in categories:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        category.id,
                        category.name,
                        category.description,
                        f"{category.status}",
                        "Edit",
                        "Delete"
                    ),
                    tags=(category.id,)
                )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading categories: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            category_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 6:  # Delete column
                self.delete_category(category_id)
            elif col_num == 5:  # Edit column
                self.edit_category(category_id)

    def edit_category(self, category_id):
        """Edit category details."""
        session = Session()
        category = session.query(Category).filter_by(id=category_id).first()
        session.close()

        if category:
            Messagebox.show_info(
                message=f"Editing Category ID: {category.id}",
                title="Edit Category",
                parent=self
            )
            # Implement edit functionality here
            self.window_manager.create_window("Edit Category", CreateCategoryView, existing_category=category)

    def delete_category(self, category_id):
        """Delete category by ID with confirmation."""
        try:
            session = Session()
            category_to_delete = session.query(Category).filter_by(id=category_id).first()

            if category_to_delete:
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete category '{category_to_delete.name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(category_to_delete)
                    session.commit()
                    self.load_categories()

                    Messagebox.show_info(
                        message="Category deleted successfully!",
                        title="Success",
                        parent=self
                    )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting category: {str(e)}",
                title="Error",
                parent=self
            )
