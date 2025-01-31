import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_renter_profile import ShopRenterProfile
from utils.database import Session


class ShopRenterListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.create_list()

    def create_list(self):
        # """Creates the list view for shop renters."""
        # ttk.Label(self, text="Shop Renters List", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(pady=(0, 20))

        # Define the columns for Treeview
        columns = ("ID", "Renter Name", "Email", "Phone", "Active Status", "Actions")
        
        # Create the Treeview widget
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure the columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Renter Name", text="Renter Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Active Status", text="Active Status")
        self.tree.heading("Actions", text="Actions")

        self.tree.column("ID", width=50)
        self.tree.column("Renter Name", width=150)
        self.tree.column("Email", width=150)
        self.tree.column("Phone", width=120)
        self.tree.column("Active Status", width=100)
        self.tree.column("Actions", width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack Treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load the renters from the database
        self.load_renters()

    def load_renters(self):
        """Loads the shop renters from the database and displays them in the Treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            renters = session.query(ShopRenterProfile).all()

            for renter in renters:
                active_status = "Active" if renter.active_status == 1 else "Inactive"
                # Insert renter data into the Treeview
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        renter.id,
                        renter.renter_name,
                        renter.email,
                        renter.phone,
                        active_status,
                        # Action buttons (Edit and Delete)
                        ""
                    )
                )

                # Add Edit and Delete buttons dynamically
                self.tree.tag_bind(self.tree.get_children()[-1], "<ButtonRelease-1>", lambda event, renter=renter: self.show_actions(event, renter))

            session.close()

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading shop renters: {str(e)}",
                title="Error",
                parent=self
            )

    def show_actions(self, event, renter):
        """Display action buttons (Edit and Delete) on click"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            # Action buttons
            edit_button = ttk.Button(self, text="Edit", bootstyle="info-outline", command=lambda: self.edit_renter(renter))
            delete_button = ttk.Button(self, text="Delete", bootstyle="danger-outline", command=lambda: self.delete_renter(renter))

            edit_button.place(x=300, y=event.y + 5)  # Adjust position for the button
            delete_button.place(x=400, y=event.y + 5)

    def edit_renter(self, renter):
        """Edit renter details."""
        print(f"Editing renter: {renter.id}")

    def delete_renter(self, renter):
        """Delete renter from the database."""
        try:
            session = Session()
            session.delete(renter)
            session.commit()
            session.close()

            # Reload the list after deleting the renter
            for widget in self.winfo_children():
                widget.destroy()
            self.create_list()
            ttk.dialogs.Messagebox.show_info(message="Shop renter deleted successfully!", title="Success", parent=self)
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(message=f"Error deleting renter: {str(e)}", title="Error", parent=self)

