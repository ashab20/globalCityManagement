import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_owner_profile import ShopOwnerProfile
from utils.database import Session


class ListShopOwnerView(ttk.Frame):
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

        # Create shop owner list
        self.create_owner_list()

    def create_owner_list(self):
        """Creates the shop owner list view."""
        # Title
        # ttk.Label(
        #     self,
        #     text="Shop Owner List",
        #     font=("Helvetica", 16, "bold"),
        #     bootstyle="primary"
        # ).pack(pady=(0, 20))

        # Create treeview
        columns = ("ID", "Name", "Phone", "Email", "Address", "NID Number", "Status")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Owner Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        self.tree.heading("NID Number", text="NID Number")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Phone", width=120)
        self.tree.column("Email", width=150)
        self.tree.column("Address", width=200)
        self.tree.column("NID Number", width=100)
        self.tree.column("Status", width=80)

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

        # Load shop owners
        self.load_shop_owners()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_shop_owners,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

    def load_shop_owners(self):
        """Load shop owners from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            owners = session.query(ShopOwnerProfile).all()

            for owner in owners:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        owner.id,
                        owner.ownner_name,
                        owner.phone,
                        owner.email,
                        owner.address,
                        owner.nid_number,
                        "Active" if owner.active_status == 1 else "Inactive"
                    )
                )

            session.close()

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading shop owners: {str(e)}",
                title="Error",
                parent=self
            )
