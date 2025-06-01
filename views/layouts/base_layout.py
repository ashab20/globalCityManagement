import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class BaseLayout(ttk.Window):
    def __init__(self, root=None, title="Application"):
        # Initialize with theme
        super().__init__(themename="cosmo")
        
        self.title(title)
        self.geometry("1200x700")
        
        # Configure global styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Create the menu bar first
        self.create_menu_bar()

        # Create main container that will hold all windows
        self.main_container = ttk.Frame(self, bootstyle="light", padding=2)
        self.main_container.pack(fill=BOTH, expand=True)

    def create_menu_bar(self):
        """Creates a menu bar - to be implemented by child classes"""
        pass

    def show_message(self, title, message):
        """Shows a message dialog."""
        ttk.dialogs.Messagebox.show_info(
            message=message,
            title=title,
            parent=self
        )
