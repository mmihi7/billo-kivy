import os
import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import shared modules
from shared.config import Config
from shared.database import db
from shared.supabase_client import supabase
from shared.utils import Utils

# Import screens
from customer_app.screens.login_screen import LoginScreen
from customer_app.screens.dashboard_screen import DashboardScreen

class BilloCustomerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Billo - Customer"
        self.icon = "assets/icon.png"
        self.sm = ScreenManager()
        
    def build(self):
        # Initialize database
        self._init_database()
        
        # Set up screens
        self._setup_screens()
        
        # Set window size for development
        if Config.DEBUG:
            Window.size = (400, 700)
            
        return self.sm
    
    def _init_database(self):
        ""Initialize the database and create tables if they don't exist."""
        try:
            db.create_tables()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def _setup_screens(self):
        ""Set up all application screens."""
        # Register screens
        screens = [
            ('login', LoginScreen()),
            ('dashboard', DashboardScreen()),
        ]
        
        for name, screen in screens:
            self.sm.add_widget(screen)
            
        # Set initial screen
        self.sm.current = 'login'
    
    def on_stop(self):
        ""Clean up resources when the app is closed."""
        # Close database connections
        if hasattr(db, 'engine') and db.engine:
            db.engine.dispose()

if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize the app
    app = BilloCustomerApp()
    app.run()
