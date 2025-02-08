import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from models.UtilitySetting import UtilitySetting
from utils.database import Session


class ListOfUtilitySettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent

        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Create utility settings list
        self.create_utility_settings_list()

    def create_utility_settings_list(self):
        """Creates the utility settings list view."""
        columns = ("ID", "Utility Name", "Rate", "Remarks", "Edit", "Delete")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Utility Name", text="Utility Name")
        self.tree.heading("Rate", text="Rate")
        self.tree.heading("Remarks", text="Remarks")
        self.tree.heading("Edit", text="Edit")
        self.tree.heading("Delete", text="Delete")

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Utility Name", width=200, anchor="w")
        self.tree.column("Rate", width=100, anchor="center")
        self.tree.column("Remarks", width=250, anchor="w")
        self.tree.column("Edit", width=75, anchor="center")
        self.tree.column("Delete", width=75, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load utility settings
        self.load_utility_settings()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_utility_settings,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

        # Bind click events
        self.tree.bind("<Button-1>", self.on_item_click)

    def load_utility_settings(self):
        """Load utility settings from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            utilities = session.query(UtilitySetting).all()

            for utility in utilities:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        utility.id,
                        utility.utility_name,
                        f"{utility.utility_rate:.2f}",
                        utility.remarks or "N/A",
                        "Edit",
                        "Delete"
                    ),
                    tags=(utility.id,)
                )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error loading utilities: {str(e)}",
                title="Error",
                parent=self
            )

    def on_item_click(self, event):
        """Handle click events on the treeview."""
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if row and column:
            utility_id = self.tree.item(row, "tags")[0]
            col_num = int(column.replace('#', ''))

            if col_num == 6:  # Delete column
                self.delete_utility_setting(utility_id)
            elif col_num == 5:  # Edit column
                self.edit_utility_setting(utility_id)

    def edit_utility_setting(self, utility_id):
        """Edit utility setting details."""
        session = Session()
        utility = session.query(UtilitySetting).filter_by(id=utility_id).first()
        session.close()

        if utility:
            Messagebox.show_info(
                message=f"Editing Utility ID: {utility.id}",
                title="Edit Utility Setting",
                parent=self
            )
            # Implement edit functionality here

    def delete_utility_setting(self, utility_id):
        """Delete utility setting by ID with confirmation."""
        try:
            session = Session()
            utility_to_delete = session.query(UtilitySetting).filter_by(id=utility_id).first()

            if utility_to_delete:
                result = Messagebox.show_question(
                    message=f"Are you sure you want to delete utility '{utility_to_delete.utility_name}'?",
                    title="Confirm Delete",
                    parent=self,
                    buttons=["Yes:primary", "No:secondary"]
                )

                if result == "Yes":
                    session.delete(utility_to_delete)
                    session.commit()
                    self.load_utility_settings()

                    Messagebox.show_info(
                        message="Utility setting deleted successfully!",
                        title="Success",
                        parent=self
                    )

            session.close()
        except Exception as e:
            Messagebox.show_error(
                message=f"Error deleting utility: {str(e)}",
                title="Error",
                parent=self
            )
