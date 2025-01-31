import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.shop_allocation import ShopAllocation
from utils.database import Session


class ListShopAllocationView(ttk.Frame):
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

        # Create shop allocation list
        self.create_allocation_list()

    def create_allocation_list(self):
        """Creates the shop allocation list view."""
        # Title
        # ttk.Label(
        #     self,
        #     text="Shop Allocation List",
        #     font=("Helvetica", 16, "bold"),
        #     bootstyle="primary"
        # ).pack(pady=(0, 20))

        # Create treeview
        columns = ("ID", "Shop Profile ID", "Renter Profile ID", "From Year", "From Month", "To Year", "To Month", "Status")
        self.tree = ttk.Treeview(
            self,
            bootstyle="primary",
            columns=columns,
            show="headings",
            height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Shop Profile ID", text="Shop Profile ID")
        self.tree.heading("Renter Profile ID", text="Renter Profile ID")
        self.tree.heading("From Year", text="From Year")
        self.tree.heading("From Month", text="From Month")
        self.tree.heading("To Year", text="To Year")
        self.tree.heading("To Month", text="To Month")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=50)
        self.tree.column("Shop Profile ID", width=120)
        self.tree.column("Renter Profile ID", width=120)
        self.tree.column("From Year", width=80)
        self.tree.column("From Month", width=80)
        self.tree.column("To Year", width=80)
        self.tree.column("To Month", width=80)
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

        # Load shop allocations
        self.load_shop_allocations()

        # Add refresh button
        ttk.Button(
            self,
            text="Refresh",
            command=self.load_shop_allocations,
            bootstyle="primary-outline",
            width=20
        ).pack(pady=(10, 0))

    def load_shop_allocations(self):
        """Load shop allocations from the database."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            session = Session()
            allocations = session.query(ShopAllocation).all()

            for allocation in allocations:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        allocation.id,
                        allocation.shop_profile_id,
                        allocation.renter_profile_id,
                        allocation.from_year,
                        allocation.from_month,
                        allocation.to_year,
                        allocation.to_month,
                        "Active" if allocation.close_status == 0 else "Closed"
                    )
                )

            session.close()

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                message=f"Error loading shop allocations: {str(e)}",
                title="Error",
                parent=self
            )
