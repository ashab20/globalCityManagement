import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from models.UtilitySetting import UtilitySetting
from utils.database import Session
from views.utilities.create_utilities import CreateUtilitySettingView
from models.acc_head_of_accounts import AccHeadOfAccounts

class ListUtilitiesView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.load_utilities()
        self.bind_events()

    def create_widgets(self):
        """Create and arrange UI components"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview with scrollbars
        self.tree = ttk.Treeview(
            main_frame,
            columns=("Utility Name", "Rate", "Unit", "Head Name", "Remarks", "Actions"),
            show="headings",
            selectmode="browse",
            height=15
        )

        # Configure columns
        columns = {
            "Utility Name": {"width": 150, "anchor": "w"},
            "Rate": {"width": 100, "anchor": "e"},
            "Unit": {"width": 80, "anchor": "center"},
            "Head Name": {"width": 150, "anchor": "w"},
            "Remarks": {"width": 200, "anchor": "w"},
            "Actions": {"width": 120, "anchor": "center"}
        }
        
        for col, config in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, **config)

        # Scrollbars
        y_scroll = ttk.Scrollbar(main_frame, orient=VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(main_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="Add New",
            command=self.add_new_utility,
            bootstyle="success"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_utilities,
            bootstyle="primary"
        ).pack(side="right", padx=5)

    def bind_events(self):
        """Bind UI events"""
        self.tree.bind("<Button-1>", self.on_tree_click)

    def load_utilities(self):
        """Load utilities from database"""
        self.tree.delete(*self.tree.get_children())
        
        session = Session()
        try:
            utilities = session.query(
                UtilitySetting,
                AccHeadOfAccounts.head_name
            ).join(
                AccHeadOfAccounts,
                UtilitySetting.releted_head_id == AccHeadOfAccounts.id,
                isouter=True
            ).all()
            
            for utility, head_name in utilities:
                self.tree.insert(
                    "", 
                    "end", 
                    values=(
                        utility.utility_name,
                        f"{utility.utility_rate:,.2f}",
                        utility.utility_unit,
                        head_name or "N/A",
                        utility.remarks or "",
                        "Edit | Delete"
                    ),
                    tags=(utility.id,)
                )
            
            self.tree.tag_configure("clickable", foreground="#007bff")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load utilities: {str(e)}")
        finally:
            session.close()

    def on_tree_click(self, event):
        """Handle clicks on the treeview"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if column == "#6":  # Actions column
                item_id = self.tree.item(item, "tags")[0]
                col_bbox = self.tree.bbox(item, column="#6")
                
                if col_bbox:
                    # Calculate click position relative to column
                    click_x = event.x - col_bbox[0]
                    if click_x < col_bbox[2]/2:
                        self.edit_utility(item_id)
                    else:
                        self.delete_utility(item_id)

    def add_new_utility(self):
        """Open new utility creation window"""
        add_window = ttk.Toplevel(self)
        add_window.title("Add New Utility")
        add_window.geometry("500x400")
        
        add_view = CreateUtilitySettingView(add_window)
        add_view.pack(fill="both", expand=True)
        
        add_view.save_button.configure(
            command=lambda: [self.load_utilities(), add_window.destroy()]
        )

    def edit_utility(self, item_id):
        """Open utility editing window"""
        session = Session()
        try:
            utility = session.query(UtilitySetting).get(item_id)
            if utility:
                edit_window = ttk.Toplevel(self)
                edit_window.title("Edit Utility")
                edit_window.geometry("500x400")
                
                edit_view = CreateUtilitySettingView(edit_window, existing_utility=utility)
                edit_view.pack(fill="both", expand=True)
                
                edit_view.save_button.configure(
                    command=lambda: [self.load_utilities(), edit_window.destroy()]
                )
        finally:
            session.close()

    def delete_utility(self, item_id):
        """Delete selected utility"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this utility?"):
            session = Session()
            try:
                utility = session.query(UtilitySetting).get(item_id)
                if utility:
                    session.delete(utility)
                    session.commit()
                    self.load_utilities()
                    messagebox.showinfo("Success", "Utility deleted successfully.")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Could not delete utility: {str(e)}")
            finally:
                session.close()