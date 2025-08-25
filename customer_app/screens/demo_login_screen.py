"""
Demo Login Screen for Billo Customer App
Handles demo mode authentication without requiring real credentials
"""

import logging
import logging
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

# Set up logging
logger = logging.getLogger(__name__)

Builder.load_string('''
<DemoLoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(24)
        
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(8)
            size_hint_y: None
            height: self.minimum_height
            pos_hint: {'center_y': 0.5}
            
            MDLabel:
                text: 'Demo Login'
                font_style: 'H4'
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
                
            MDTextField:
                id: username
                hint_text: 'Username'
                helper_text: 'Enter: demo'
                helper_text_mode: 'on_focus'
                size_hint_x: 0.8
                pos_hint: {'center_x': 0.5}
                on_text_validate: password.focus = True
                
            MDTextField:
                id: password
                hint_text: 'Password'
                helper_text: 'Enter: demo'
                helper_text_mode: 'on_focus'
                password: True
                size_hint_x: 0.8
                pos_hint: {'center_x': 0.5}
                on_text_validate: root.try_login()
            
            BoxLayout:
                size_hint: (None, None)
                size: (dp(200), dp(48))
                pos_hint: {'center_x': 0.5}
                spacing: dp(16)
                
                MDRaisedButton:
                    text: 'Login'
                    size_hint_x: 1
                    on_release: root.try_login()
                    
            MDLabel:
                text: 'Use "demo" for both username and password'
                theme_text_color: 'Secondary'
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
                font_style: 'Caption'
''')

class DemoLoginScreen(Screen):
    """Screen for demo mode login with simple credentials."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'demo_login'
        self.dialog = None
        self.demo_username = 'demo'
        self.demo_password = 'demo'
        
        # Set demo mode flag when this screen is created
        app = App.get_running_app()
        app.demo_mode = True
    
    def on_pre_enter(self):
        """Called before the screen is displayed."""
        # Reset any previous state
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
    
    def on_enter(self):
        """Auto-focus the username field when screen is shown."""
        if hasattr(self, 'ids') and 'username' in self.ids:
            self.ids.username.focus = True
    
    def try_login(self):
        """Check demo credentials and proceed to demo dashboard."""
        try:
            username = self.ids.username.text.strip()
            password = self.ids.password.text
            
            if username == self.demo_username and password == self.demo_password:
                self._navigate_to_demo_dashboard()
            else:
                self._show_error("Invalid credentials. Use 'demo' for both username and password.")
        except Exception as e:
            logger.error(f"Error in try_login: {e}", exc_info=True)
            self._show_error(f"Login error: {str(e)}")
    
    def _navigate_to_demo_dashboard(self):
        """Navigate to the demo dashboard screen."""
        try:
            app = App.get_running_app()
            
            # Add demo dashboard screen if it doesn't exist
            if 'demo_dashboard' not in app.sm.screen_names:
                logger.info("Creating demo dashboard screen...")
                from customer_app.screens.demo_dashboard_screen import DemoDashboardScreen
                demo_dashboard = DemoDashboardScreen()
                app.sm.add_widget(demo_dashboard)
            
            # Navigate to demo dashboard
            logger.info("Switching to demo dashboard...")
            app.sm.current = 'demo_dashboard'
            logger.info(f"Current screen: {app.sm.current}")
            
        except Exception as e:
            logger.error(f"Error navigating to demo dashboard: {e}", exc_info=True)
            self._show_error(f"Failed to load demo dashboard")
    
    def _show_error(self, message):
        """Show error message to user."""
        if not hasattr(self, 'dialog'):
            self.dialog = None
            
        if self.dialog:
            self.dialog.dismiss()
            
        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def show_loading(self, message="Loading..."):
        """Show a loading dialog."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title=message,
            type="custom",
            auto_dismiss=False,
            buttons=[],
        )
        self.dialog.open()
    
    def dismiss_loading(self):
        """Dismiss the loading dialog."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
            self.dialog = None
