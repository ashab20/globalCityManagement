import ttkbootstrap as ttk
from views.login_view import LoginView
from views.dashboard_view import DashboardView


class App:
    def __init__(self):
        # Create root window
        self.root = ttk.Window(
            title="Global City Management",
            themename="litera",
            size=(1024, 768),
            position=(100, 100),
            minsize=(800, 600)
        )
        
        # Configure style
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        
        # Show login view
        self.show_login()
        
        # Center window
        self.root.place_window_center()
    
    def show_login(self):
        """Show login view."""
        if hasattr(self, 'current_view'):
            self.current_view.destroy()
        
        # Configure window for login
        self.root.title("Global City Management - Login")
        self.root.geometry("400x500")  # Increased height
        self.root.place_window_center()
        
        self.current_view = LoginView(self.root, self.on_login)
        self.current_view.pack(fill="both", expand=True)
    
    def show_dashboard(self):
        """Show dashboard view."""
        if hasattr(self, 'current_view'):
            self.current_view.destroy()
        
        # Configure window for dashboard
        self.root.title("Global City Management - Dashboard")
        self.root.geometry("1024x768")
        self.root.place_window_center()
        
        self.current_view = DashboardView(self.root, self.on_logout)
        self.current_view.pack(fill="both", expand=True)
    
    def on_login(self):
        """Handle successful login."""
        self.show_dashboard()
    
    def on_logout(self):
        """Handle logout."""
        self.show_login()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
