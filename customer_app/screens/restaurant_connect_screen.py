"""
Restaurant Connect Screen for Billo Customer App
Handles the initial connection to a restaurant
"""

import logging
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

# Set up logging
logger = logging.getLogger(__name__)

Builder.load_string('''
#:import Window kivy.core.window.Window

<RestaurantConnectScreen>:
    # No back button for this screen
    
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(24)
        size_hint_y: None
        height: Window.height
        
        # Add some top padding for better visual balance
        Widget:
            size_hint_y: 0.15
        
        # Main content area
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.8
            spacing: dp(32)
            padding: [dp(16), dp(0), dp(16), dp(0)]
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            
            # Title and subtitle
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: 0.3
                spacing: dp(8)
                
                MDLabel:
                    text: 'Connect to a Restaurant'
                    font_style: 'H4'
                    halign: 'center'
                    size_hint_y: None
                    height: self.texture_size[1]
                    font_size: '24sp'
                    
                MDLabel:
                    text: 'Scan a restaurant QR code to start ordering'
                    theme_text_color: 'Secondary'
                    halign: 'center'
                    size_hint_y: None
                    height: self.texture_size[1]
                    font_size: '16sp'
            
            # Main action button
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: 0.4
                spacing: dp(24)
                
                MDRaisedButton:
                    id: scan_btn
                    text: 'Scan QR Code'
                    size_hint: None, None
                    size: dp(200), dp(48)
                    pos_hint: {'center_x': 0.5}
                    on_release: root.on_scan_pressed()
                    disabled: not root.is_android
                    disabled_text_color: 1, 1, 1, 0.7
                    disabled_opacity: 1
                    elevation_normal: 8
                    font_size: '18sp'
                    
                    MDLabel:
                        text: '(Android only)' if not root.is_android else ''
                        font_style: 'Caption'
                        theme_text_color: 'Secondary'
                        halign: 'center'
                        size_hint_y: None
                        height: self.texture_size[1]
                        pos_hint: {'center_x': 0.5, 'top': -0.1}
                        color: 1, 1, 1, 0.8
                
                # Demo button
                MDRaisedButton:
                    id: demo_btn
                    text: 'Try Demo Mode'
                    size_hint: None, None
                    size: dp(200), dp(48)
                    pos_hint: {'center_x': 0.5}
                    on_release: root.on_demo_pressed()
                    elevation_normal: 8
                    font_size: '18sp'
                    md_bg_color: 0.3, 0.7, 0.3, 1
                    text_color: 1, 1, 1, 1
''')

class RestaurantConnectScreen(Screen):
    """Screen for connecting to a restaurant."""
    
    is_android = BooleanProperty(platform == 'android')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
        # Disable scan button on non-Android devices
        if hasattr(self, 'ids') and 'scan_btn' in self.ids:
            self.ids.scan_btn.disabled = not self.is_android
            self.ids.scan_btn.md_bg_color = (0.2, 0.6, 0.8, 1) if self.is_android else (0.5, 0.5, 0.5, 1)
    
    def on_scan_pressed(self):
        """Handle scan button press."""
        if not self.is_android:
            self.show_error("Not Supported", "QR code scanning is only available on Android devices.")
            return
        
        app = App.get_running_app()
        if 'qr_scanner' in app.sm.screen_names:
            app.sm.remove_widget(app.sm.get_screen('qr_scanner'))
            
            # Now switch to the scanner
            self.manager.switch_screen('qr_scanner')
    
    def on_demo_pressed(self):
        """Handle demo button press - navigate to demo login screen."""
        try:
            app = App.get_running_app()
            app.demo_mode = True
            
            # Add demo login screen if not exists
            if 'demo_login' not in app.sm.screen_names:
                from customer_app.screens.demo_login_screen import DemoLoginScreen
                demo_login = DemoLoginScreen()
                app.sm.add_widget(demo_login)
                logger.info("Added demo login screen")
            
            # Navigate to demo login
            logger.info("Switching to demo login screen...")
            app.sm.current = 'demo_login'
            
        except Exception as e:
            logger.error(f"Error in on_demo_pressed: {e}", exc_info=True)
            self.show_error(f"Failed to start demo: {str(e)}")
    
    def show_error(self, message):
        """Show an error message."""
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
