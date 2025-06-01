from tkinter import StringVar, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class TopMenuView(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, bootstyle=SECONDARY, padding=5)

        self.root = root
        self.title("Desktop Application Dashboard")
        self.geometry("1200x700")

        self.create_widgets()
        """Creates a top menu with large icons."""
        top_menu = ttk.Frame(self, padding=5)
        top_menu.pack(fill=X, side=TOP)

        # Add menu items with icons
        icons = [
            {"text": "Home", "icon": "home"},
            {"text": "Users", "icon": "user"},
            {"text": "Settings", "icon": "gear"},
            {"text": "Reports", "icon": "chart-line"},
            {"text": "Logout", "icon": "log-out"},
        ]

        for item in icons:
            icon = ttk.Label(top_menu, text=item["text"], compound=TOP, padding=10)
            icon.pack(side=LEFT, padx=10)