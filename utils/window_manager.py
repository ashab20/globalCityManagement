import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class InternalWindow(ttk.Frame):
    DEFAULT_ICONS = {
        "User Management": "👤",
        "Shop Management": "🏪",
        "Accounting Management": "💰",
        "Bill and Collections": "📥",
        "Inventory": "📦",
        "Report": "📊",
        "Settings": "⚙️",
        "Help": "❓"
    }

    def __init__(self, parent, title, window_manager):
        super().__init__(parent)
        self.parent = parent
        self.window_manager = window_manager
        
        # Configure styles
        style = ttk.Style()
        style.configure("Internal.TFrame", background="#f8f9fa", borderwidth=1, relief="solid")
        style.configure("Title.TFrame", background="#4361ee")
        style.configure("Title.TLabel", background="#4361ee", foreground="white", font=("Helvetica", 10, "bold"))
        style.configure("Content.TFrame", background="white", borderwidth=1, relief="solid")
        
        # Main frame with border
        self.main_frame = ttk.Frame(self, style="Internal.TFrame", padding=1)
        self.main_frame.pack(fill="both", expand=True)
        
        # Title bar with modern blue color
        self.title_bar = ttk.Frame(self.main_frame, style="Title.TFrame", height=30)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        # Title label
        self.title_label = ttk.Label(
            self.title_bar,
            text=title,
            style="Title.TLabel",
            padding=(10, 0)
        )
        self.title_label.pack(side="left")
        
        # Close button
        self.close_button = ttk.Button(
            self.title_bar,
            text="×",
            bootstyle="danger",
            command=self._on_close,
            width=3
        )
        self.close_button.pack(side="right")
        
        # Content frame with white background and border
        self.content = ttk.Frame(self.main_frame, style="Content.TFrame", padding=2)
        self.content.pack(fill="both", expand=True)
        
        # Initialize drag variables
        self._drag_data = {"x": 0, "y": 0, "dragging": False}
        
        # Bind events for dragging
        self.title_bar.bind("<Button-1>", self._on_drag_start)
        self.title_bar.bind("<B1-Motion>", self._on_drag_motion)
        self.title_bar.bind("<ButtonRelease-1>", self._on_drag_stop)
        self.title_label.bind("<Button-1>", self._on_drag_start)
        self.title_label.bind("<B1-Motion>", self._on_drag_motion)
        self.title_label.bind("<ButtonRelease-1>", self._on_drag_stop)
        
        # Bind click events for focus
        self.bind_all("<Button-1>", self._check_focus, True)
    
    def _on_drag_start(self, event):
        """Start dragging the window."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["dragging"] = True
        self.lift()
    
    def _on_drag_motion(self, event):
        """Handle window dragging."""
        if not self._drag_data["dragging"]:
            return
            
        # Calculate the distance moved
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        
        # Get current position
        x = self.winfo_x() + dx
        y = self.winfo_y() + dy
        
        # Keep window within parent bounds
        parent = self.parent
        max_x = parent.winfo_width() - self.winfo_width()
        max_y = parent.winfo_height() - self.winfo_height()
        
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))
        
        # Move window
        self.place(x=x, y=y)
    
    def _on_drag_stop(self, event):
        """Stop dragging the window."""
        self._drag_data["dragging"] = False
    
    def _check_focus(self, event):
        """Check if window should be brought to front."""
        try:
            if isinstance(event.widget, (ttk.Button, ttk.Entry)):
                return
                
            # Check if window still exists and is properly initialized
            if not self.winfo_exists():
                return
                
            # Check if click is within this window
            x = self.winfo_rootx()
            y = self.winfo_rooty()
            w = self.winfo_width()
            h = self.winfo_height()
            
            if (x <= event.x_root <= x + w and 
                y <= event.y_root <= y + h):
                self.lift()
        except Exception as e:
            # Silently handle any window-related errors
            pass
    
    def _on_close(self):
        """Handle window close."""
        self.window_manager.remove_window(self)
        self.destroy()


class WindowManager:
    def __init__(self, parent):
        self.parent = parent
        self.windows = []
        
        # Configure global styles
        style = ttk.Style()
        
        # Configure modern colors for widgets
        style.configure("TEntry", fieldbackground="#f8f9fa", bordercolor="#4361ee")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("primary.TButton", background="#4361ee")
        style.configure("danger.TButton", background="#ef233c")
        style.configure("TLabel", font=("Helvetica", 10))
        
        # Configure Treeview colors
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground="black",
            font=("Helvetica", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#4361ee",
            foreground="white",
            font=("Helvetica", 10, "bold")
        )
        style.map(
            "Treeview",
            background=[("selected", "#4361ee")],
            foreground=[("selected", "white")]
        )
    
    def create_window(self, title, view_class, **kwargs):
        """Creates a new internal window."""
        # Create window container
        window = InternalWindow(self.parent, title, self)
        
        # Create view inside window
        view = view_class(window.content, **kwargs)
        view.pack(fill="both", expand=True)
        
        # Position window with cascade offset
        offset = len(self.windows) * 30
        window.place(x=50 + offset, y=50 + offset, width=700, height=600)
        
        # Add to windows list and bring to front
        self.windows.append(window)
        window.lift()
        
        return window
    
    def remove_window(self, window):
        """Remove window from manager."""
        if window in self.windows:
            self.windows.remove(window)
    
    def close_all(self):
        """Close all windows."""
        for window in self.windows[:]:
            window.destroy()
        self.windows.clear()
