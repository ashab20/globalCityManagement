import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.unit import Unit
from utils.database import Session
from views.unit.create_unit import CreateUnitView


class UnitListView(ttk.Frame):
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

        # Create unit list
        self.create_unit_list()

    def create_unit_list(self):
        """Creates the unit list view."""
        columns = ("ID", "Name", "Status", "Edit", "Delete")
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
        self.tree.heading("Status", text="Status")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=100, anchor="w")
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

        # Load units
        self.load_units()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_units,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)

    def load_units(self):
        """Load units from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            units = session.query(Unit).all()

            for unit in units:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        unit.id,
                        unit.unit_name,
                        "Active" if unit.status == 1 else "Inactive",
                        "Edit",
                        "Delete"
                    ),
                    tags=(unit.id,)
                )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading units: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            unit_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 5:  # Delete column
                self.delete_unit(unit_id)
            elif col_num == 4:  # Edit column
                self.edit_unit(unit_id)

    def edit_unit(self, unit_id):
        """Edit unit details."""
        session = Session()
        unit = session.query(Unit).filter_by(id=unit_id).first()
        session.close()

        if unit:
            # Create edit window
            edit_window = ttk.Toplevel(self)
            edit_window.title(f"Edit Unit - {unit.unit_name}")
            edit_window.geometry("500x300")
            
            edit_view = CreateUnitView(edit_window, existing_unit=unit)
            edit_view.pack(fill="both", expand=True)
            
            # Update save button to refresh list
            edit_view.save_button.configure(
                command=lambda: [
                    edit_view.save_unit(),
                    edit_window.destroy(),
                    self.load_units()
                ]
            )

    def delete_unit(self, unit_id):
        """Delete unit by ID with confirmation."""
        try:
            session = Session()
            unit_to_delete = session.query(Unit).filter_by(id=unit_id).first()

            if unit_to_delete:
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete unit '{unit_to_delete.unit_name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(unit_to_delete)
                    session.commit()
                    self.load_units()

                    Messagebox.show_info(
                        message="Unit deleted successfully!",
                        title="Success",
                        parent=self
                    )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting unit: {str(e)}",
                title="Error",
                parent=self
            )
