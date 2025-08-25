"""
QR Code Scanner Screen for Billo Customer App
Handles scanning restaurant QR codes to open new tabs

On Android: Uses device camera for QR scanning
On other platforms: Uses a simulator for testing
"""

import logging
import os
import sys
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.utils import platform

# Import the QR simulator for non-Android platforms
if platform == 'android':
    # Android-specific imports
    try:
        from kivy.garden.zbarcam import ZBarCam
        from pyzbar.pyzbar import ZBarSymbol
        from android.permissions import request_permissions, Permission, check_permission
        from android import mActivity
    except ImportError as e:
        logging.error(f"Failed to import Android modules: {e}")
        platform = 'desktop'  # Fall back to simulator if imports fail
else:
    # Non-Android platforms will use the simulator
    from customer_app.qr_simulator import QRSimulator

# Set up logging
logger = logging.getLogger(__name__)

# Load the KV layout for this screen
Builder.load_file('customer_app/screens/qr_scanner_screen.kv')

class QRScannerScreen(Screen):
    """Screen for scanning restaurant QR codes."""
    
    scan_result = StringProperty('')
    demo_mode = BooleanProperty(False)
    has_camera_permission = BooleanProperty(False)
    is_scanning = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        self.demo_mode = kwargs.pop('demo_mode', False)
        super().__init__(**kwargs)
        self.qr_simulator = None
        self.scan_interval = None
        self.dialog = None  # Add dialog attribute
        
        # Check camera permission on Android
        if platform == 'android':
            self.check_camera_permission()
        else:
            # On non-Android, use demo mode by default
            self.has_camera_permission = False
            self.demo_mode = True
            self.qr_simulator = QRSimulator(self.on_qr_code_scanned)
        
    def on_enter(self, *args):
        """Called when the screen is displayed."""
        super().on_enter(*args)
        
        # Show appropriate UI based on platform and demo mode
        if self.demo_mode:
            # Show demo UI
            if platform == 'android':
                self.stop_scanning()
            return
            
        # Handle non-demo mode
        if platform == 'android':
            self.start_scanning()
        elif self.qr_simulator:
            # On non-Android, show the demo UI by default
            self.demo_mode = True
            
    def on_demo_mode(self, instance, value):
        """Handle changes to demo mode."""
        if value and platform == 'android':
            self.stop_scanning()
        
    def on_leave(self):
        """Clean up when leaving the screen."""
        self.stop_scanning()
        
    def check_camera_permission(self):
        """Check and request camera permissions if needed."""
        if platform != 'android':
            self.has_camera_permission = False
            self.demo_mode = True
            return
            
        from android.permissions import Permission, check_permission, request_permissions
        
        def callback(permissions, results):
            if all(results):
                self.has_camera_permission = True
            else:
                self.has_camera_permission = False
                self.demo_mode = True
                self.show_error_dialog("Permission Required", "Camera permission is required to scan QR codes.")
        
        if check_permission(Permission.CAMERA):
            self.has_camera_permission = True
        else:
            request_permissions([Permission.CAMERA], callback)
            
        has_permission = check_permission(Permission.CAMERA)
        if not has_permission:
            self.request_camera_permission()
        else:
            self.has_camera_permission = True
            self.start_scanning()
    
    def request_camera_permission(self):
        """Request camera permission on Android."""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            
            def callback(permission, results):
                if all([res for res in results]):
                    self.has_camera_permission = True
                    self.start_scanning()
                else:
                    self.show_error_dialog(
                        "Camera Permission Required",
                        "Camera permission is required to scan QR codes.\n\n"
                        "Please enable it in your device settings."
                    )
            
            request_permissions([Permission.CAMERA], callback)
    
    def start_scanning(self):
        """Start the QR code scanning process."""
        if self.is_scanning:
            return
            
        if platform != 'android':
            # On non-Android platforms, show the simulator if not already showing
            if self.qr_simulator and not self.qr_simulator.popup:
                self.qr_simulator.show_simulator()
            return
            
        if not self.has_camera_permission:
            self.check_camera_permission()
            return
            
        self.is_scanning = True
        
        try:
            # Initialize ZBarCam for QR code scanning
            if not hasattr(self, 'zbarcam') and 'camera_container' in self.ids:
                self.zbarcam = ZBarCam(
                    code_types=[
                        ZBarSymbol.QRCODE,
                        ZBarSymbol.EAN13,
                        ZBarSymbol.UPCA,
                        ZBarSymbol.EAN8
                    ]
                )
                self.zbarcam.bind(symbols=self.on_symbols)
                self.ids.camera_container.add_widget(self.zbarcam)
                
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            self.show_error_dialog("Camera Error", "Failed to access the camera.")
            self.is_scanning = False
    
    def on_symbols(self, instance, symbols):
        """Handle detected QR codes."""
        if not symbols:
            return
            
        # Get the first detected symbol
        symbol = symbols[0]
        qr_data = symbol.data.decode('utf-8')
        
        # Process the QR code data
        self.on_qr_scanned(qr_data)
    
    def stop_scanning(self):
        """Stop the QR code scanning process."""
        self.is_scanning = False
        
        # Clean up camera resources
        if hasattr(self, 'zbarcam') and self.zbarcam:
            try:
                self.zbarcam.play = False
                self.zbarcam.parent.remove_widget(self.zbarcam)
                self.zbarcam = None
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
    
    def on_qr_code_scanned(self, qr_data):
        """Handle scanned QR code data."""
        if not qr_data:
            return
            
        if qr_data.startswith('restaurant:'):
            self.process_restaurant_qr(qr_data.replace('restaurant:', ''))
        else:
            self.show_error_dialog("Invalid QR Code", "Please scan a valid restaurant QR code.")
            
        # If in demo mode, navigate to dashboard after a short delay
        if self.demo_mode:
            Clock.schedule_once(lambda dt: self.switch_to_dashboard(), 1.5)
            
    def switch_to_dashboard(self):
        """Switch to the dashboard screen."""
        if hasattr(self, 'app') and hasattr(self.app, 'root'):
            self.app.root.current = 'dashboard'
            
        # If we're on Android, stop the camera
        if platform == 'android' and self.zbarcam:
            self.zbarcam.play = False
    
    def process_restaurant_qr(self, restaurant_id):
        """Process a scanned restaurant QR code."""
        # Show loading dialog
        self.show_loading_dialog("Loading restaurant information...")
        
        # In a real app, you would fetch restaurant data from your backend
        # For now, we'll simulate a network request
        Clock.schedule_once(
            lambda dt: self._fetch_restaurant_info(restaurant_id),
            1.0  # Simulate network delay
        )
    
    def _fetch_restaurant_info(self, restaurant_id):
        """Fetch restaurant information from the backend."""
        try:
            # In a real app, you would make an API call here
            # For example:
            # restaurant_data = self.app.supabase.table('restaurants')\
            #     .select('*')\
            #     .eq('id', restaurant_id)\
            #     .single()
            #     .execute()
            
            # Simulated restaurant data
            restaurant_data = {
                'id': restaurant_id,
                'name': f'Restaurant {restaurant_id.upper()}',
                'description': 'A great place to enjoy your meal',
                'open_hours': '10:00 AM - 10:00 PM',
                'contact': '+1234567890',
                'address': '123 Food Street, City'
            }
            
            # Dismiss loading dialog
            if self.dialog:
                self.dialog.dismiss()
                
            # Show restaurant info
            self.show_restaurant_info(restaurant_data)
            
        except Exception as e:
            logger.error(f"Error fetching restaurant info: {e}")
            if self.dialog:
                self.dialog.dismiss()
            self.show_error_dialog("Error", "Failed to load restaurant information. Please try again.")
    
    def show_restaurant_info(self, restaurant_data):
        """Display restaurant information to the user."""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDRaisedButton
        
        # Create content layout
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=dp(300)
        )
        
        # Add restaurant info
        content.add_widget(MDLabel(
            text=restaurant_data['name'],
            font_style='H5',
            halign='center'
        ))
        
        # Add restaurant details
        details = [
            f"🕒 {restaurant_data['open_hours']}",
            f"📞 {restaurant_data['contact']}",
            f"📍 {restaurant_data['address']}",
            f"\n{restaurant_data['description']}"
        ]
        
        for detail in details:
            content.add_widget(MDLabel(
                text=detail,
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(40)
            ))
        
        # Create dialog
        self.dialog = MDDialog(
            title="Restaurant Information",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CONTINUE",
                    on_release=lambda x: self._on_continue_to_menu(restaurant_data['id'])
                )
            ]
        )
        self.dialog.open()
    
    def _on_continue_to_menu(self, restaurant_id):
        """Handle continue to menu button press by creating a new tab."""
        if self.dialog:
            self.dialog.dismiss()
        
        self.show_loading_dialog("Creating your tab...")
        
        # Schedule tab creation to run in the background
        Clock.schedule_once(
            lambda dt: self._create_tab(restaurant_id),
            0.1  # Small delay to show loading dialog
        )
    
    def _create_tab(self, restaurant_id):
        """Create a new tab for the user at the restaurant."""
        try:
            # Get the current user ID
            app = App.get_running_app()
            user_id = app.auth_service.get_current_user_id()
            
            if not user_id:
                raise Exception("User not authenticated")
            
            # Get the next available tab number for this restaurant today
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # In a real app, this would be a Supabase query to get the next tab number
            # For now, we'll generate a random tab number
            import random
            tab_number = random.randint(100, 999)  # 3-digit tab number
            
            # Create the tab in the database
            # In a real app, this would be a Supabase insert
            # tab_data = {
            #     'restaurant_id': restaurant_id,
            #     'customer_id': user_id,
            #     'tab_number': tab_number,
            #     'date': today,
            #     'status': 'active'
            # }
            # result = app.supabase.table('tabs').insert(tab_data).execute()
            
            # For now, we'll just use the generated tab number
            tab_data = {
                'id': f'tab_{restaurant_id}_{tab_number}',
                'restaurant_id': restaurant_id,
                'tab_number': tab_number,
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
            # Update the dashboard with the new tab
            if hasattr(self, 'manager') and self.manager.has_screen('dashboard'):
                dashboard = self.manager.get_screen('dashboard')
                dashboard.add_new_tab(tab_data)
            
            # Show success message with tab number
            if self.dialog:
                self.dialog.dismiss()
                
            self.show_success_dialog(
                "Tab Created",
                f"Your tab number is:\n\n"
                f"## {tab_number}\n\n"
                "Please provide this number to your server.",
                on_dismiss=self.return_to_dashboard
            )
            
        except Exception as e:
            logger.error(f"Error creating tab: {e}")
            if self.dialog:
                self.dialog.dismiss()
            self.show_error_dialog(
                "Error",
                "Failed to create your tab. Please try again."
            )
    
    def show_loading_dialog(self, message):
        """Show a loading dialog with the given message."""
        if self.dialog:
            self.dialog.dismiss()
            
        self.dialog = MDDialog(
            title="Please Wait",
            text=message,
            auto_dismiss=False
        )
        self.dialog.open()
    
    def return_to_dashboard(self, *args):
        """Return to the dashboard screen."""
        if hasattr(self, 'manager') and self.manager.has_screen('dashboard'):
            self.manager.current = 'dashboard'
    
    def show_error_dialog(self, title, message):
        """Show an error dialog with the given title and message."""
        if self.dialog:
            self.dialog.dismiss()
            
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
        
    def show_success_dialog(self, title, message):
        """Show a success dialog with the given title and message."""
        if self.dialog:
            self.dialog.dismiss()
            
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def show_success_dialog(self, title, message, on_dismiss=None):
        """Show a success dialog with the given title and message."""
        if self.dialog:
            self.dialog.dismiss()
            
        def dismiss_callback(instance):
            self.dialog.dismiss()
            if on_dismiss:
                on_dismiss()
        
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=dismiss_callback
                )
            ]
        )
        self.dialog.open()
