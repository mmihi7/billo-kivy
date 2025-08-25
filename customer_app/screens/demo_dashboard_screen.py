"""
Demo Dashboard Screen for Billo Customer App
Shows demo data without requiring authentication
"""

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

Builder.load_file('customer_app/screens/demo_dashboard_screen.kv')

class DemoDashboardScreen(Screen):
    """Screen showing demo dashboard with sample data."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'demo_dashboard'
        self.dialog = None
        self.demo_data_loaded = False
    
    def on_pre_enter(self):
        """Called before the screen is displayed."""
        # Load demo data when the screen is about to be shown
        if not self.demo_data_loaded:
            Clock.schedule_once(self._load_demo_data, 0.1)
    
    def _load_demo_data(self, dt):
        """Load sample demo data."""
        try:
            logger.info("Loading demo data...")
            
            # Sample demo data
            demo_data = {
                'restaurant_name': 'Demo Restaurant',
                'table_number': 'T-001',
                'bills': [
                    {'id': 'DEMO-001', 'amount': 25.99, 'status': 'Pending', 'items': ['Pizza', 'Soda']},
                    {'id': 'DEMO-002', 'amount': 18.50, 'status': 'Paid', 'items': ['Burger', 'Fries']},
                ],
                'menu': [
                    {'name': 'Pizza', 'price': 12.99, 'category': 'Mains'},
                    {'name': 'Burger', 'price': 8.99, 'category': 'Mains'},
                    {'name': 'Fries', 'price': 3.99, 'category': 'Sides'},
                    {'name': 'Soda', 'price': 2.50, 'category': 'Drinks'},
                ]
            }
            
            # Update UI with demo data
            if hasattr(self, 'ids'):
                if 'restaurant_name' in self.ids:
                    self.ids.restaurant_name.text = demo_data['restaurant_name']
                if 'table_number' in self.ids:
                    self.ids.table_number.text = f"Table: {demo_data['table_number']}"
                
                # Update bills list
                if 'bills_list' in self.ids:
                    self.ids.bills_list.clear_widgets()
                    for bill in demo_data['bills']:
                        self.ids.bills_list.add_widget(
                            MDRaisedButton(
                                text=f"Bill {bill['id']} - ${bill['amount']} - {bill['status']}",
                                size_hint_y=None,
                                height=dp(50),
                                on_release=lambda x, b=bill: self._show_bill_details(b)
                            )
                        )
            
            self.demo_data_loaded = True
            logger.info("Demo data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading demo data: {e}", exc_info=True)
            self._show_error(f"Failed to load demo data: {str(e)}")
    
    def _show_bill_details(self, bill):
        """Show details of the selected bill."""
        try:
            items = "\n".join([f"• {item}" for item in bill['items']])
            message = (
                f"Bill ID: {bill['id']}\n"
                f"Amount: ${bill['amount']}\n"
                f"Status: {bill['status']}\n\n"
                f"Items:\n{items}"
            )
            
            self.dialog = MDDialog(
                title="Bill Details",
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="CLOSE",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()
            
        except Exception as e:
            logger.error(f"Error showing bill details: {e}", exc_info=True)
            self._show_error("Failed to show bill details")
    
    def on_logout_pressed(self):
        """Handle logout button press."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'sm') and 'restaurant_connect' in app.sm.screen_names:
                # Reset demo mode when logging out
                app.demo_mode = False
                app.sm.current = 'restaurant_connect'
        except Exception as e:
            logger.error(f"Error during logout: {e}", exc_info=True)
            self._show_error("Failed to log out")
    
    def _show_error(self, message):
        """Show error message to user."""
        if hasattr(self, 'dialog') and self.dialog:
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
