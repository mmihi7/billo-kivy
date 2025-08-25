import asyncio
import logging
import json
from datetime import datetime
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.properties import (
    StringProperty, ListProperty, NumericProperty, 
    BooleanProperty, ObjectProperty
)
from kivy.clock import Clock, mainthread
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import mainthread
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.toast import toast

# Import QR Scanner Screen
from customer_app.screens.qr_scanner_screen import QRScannerScreen

# Set up logging
logger = logging.getLogger(__name__)

class TabCard(MDCard):
    """Card widget for displaying tab information."""
    tab_id = StringProperty()
    tab_number = StringProperty()
    status = StringProperty('active')
    total = NumericProperty(0.0)
    restaurant = StringProperty('')
    created_at = StringProperty('')
    updated_at = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ripple_rad = dp(10)
        self.ripple_behavior = True
        self.elevation = 1
        self.md_bg_color = (1, 1, 1, 1)
    
    def on_release(self):
        """Handle tap on tab card."""
        from kivy.app import App
        app = App.get_running_app()
        
        # Navigate to tab details screen with tab_id
        if hasattr(app, 'sm'):
            # TODO: Implement tab details screen navigation
            print(f"Navigating to tab details: {self.tab_number}")
    
    def on_status(self, instance, value):
        """Update UI when status changes."""
        if hasattr(self, 'ids') and 'status_chip' in self.ids:
            self.ids.status_chip.text = value.upper()
            
            # Update chip color based on status
            if value == 'active':
                self.ids.status_chip.md_bg_color = [0.0, 0.59, 0.53, 1.0]  # Teal 500
            elif value == 'paid':
                self.ids.status_chip.md_bg_color = [0.3, 0.69, 0.31, 1.0]  # Green 600
            elif value == 'cancelled':
                self.ids.status_chip.md_bg_color = [0.96, 0.26, 0.21, 1.0]  # Red 500
            else:
                self.ids.status_chip.md_bg_color = [0.62, 0.62, 0.62, 1.0]  # Grey 400

class DashboardScreen(Screen):
    """Main dashboard screen showing active tabs and recent activity."""
    
    # Properties
    user_name = StringProperty("Guest")
    active_tabs = ListProperty([])
    recent_activity = ListProperty([])
    loading = BooleanProperty(False)
    last_refresh = StringProperty("")
    
    # Realtime subscription
    _realtime_subscription = None
    
    # Services
    auth_service = ObjectProperty(None)
    
    def __init__(self, auth_service=None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service
        self.dialog = None
        self._refresh_event = None
        
        # Register QR scanner screen
        if not App.get_running_app().sm.has_screen('qr_scanner'):
            qr_scanner = QRScannerScreen(name='qr_scanner')
            App.get_running_app().sm.add_widget(qr_scanner)
    
    def on_pre_enter(self):
        """Called before the screen is displayed."""
        app = App.get_running_app()
        
        # Check if we're in demo mode
        if hasattr(app, 'demo_mode') and app.demo_mode:
            # Clear any existing demo data first
            if hasattr(self, 'ids') and 'main_layout' in self.ids:
                self.ids.main_layout.clear_widgets()
            # Load demo data
            Clock.schedule_once(lambda dt: self._load_demo_data(), 0.1)
            return
            
        # Regular mode - load real data
        self.refresh_data()
        if hasattr(self, '_setup_realtime_updates'):
            self._setup_realtime_updates()
        self.last_refresh = datetime.now().strftime("%H:%M")
    
    def on_leave(self):
        """Clean up when leaving the screen."""
        if self._refresh_event:
            self._refresh_event.cancel()
        
        # Clean up realtime subscription
        self._cleanup_realtime_updates()
    
    def refresh_data(self):
        """Refresh data from the server."""
        if self.loading:
            return
            
        # Skip refresh in demo mode
        app = App.get_running_app()
        if hasattr(app, 'demo_mode') and app.demo_mode:
            return
            
        self._set_loading(True, "Refreshing...")
        self.load_user_data()
    
    def load_user_data(self):
        """Load user data and active tabs asynchronously."""
        if not self.auth_service or not self.auth_service.is_authenticated():
            self.loading = False
            return
            
        # Show loading state
        self.loading = True
        
        # Run in background
        asyncio.create_task(self._async_load_user_data())
    
    async def _async_load_user_data(self):
        """Asynchronously load user data and tabs."""
        try:
            # Get user profile
            user = self.auth_service.get_current_user()
            if user and 'user_metadata' in user:
                self._update_user_info(user['user_metadata'])
            
            # Load active tabs and recent activity in parallel
            await asyncio.gather(
                self._load_active_tabs(),
                self._load_recent_activity()
            )
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}", exc_info=True)
            self._show_error("Failed to load dashboard data. Please try again.")
        finally:
            self._set_loading(False)
    
    @mainthread
    def _update_user_info(self, user_metadata):
        """Update UI with user information."""
        if 'full_name' in user_metadata:
            self.user_name = user_metadata['full_name']
        elif 'email' in user_metadata:
            self.user_name = user_metadata['email'].split('@')[0].capitalize()
    
    async def _load_active_tabs(self):
        """Load user's active tabs from the database with related data."""
        try:
            # Get current user's ID
            user_id = self.auth_service.get_user_id()
            if not user_id:
                return
                
            # Fetch active tabs with related restaurant and order data
            response = await self.auth_service.supabase.table('tabs') \
                .select('''
                    *,
                    restaurant:restaurants (
                        id,
                        name,
                        logo_url
                    ),
                    orders (
                        id,
                        status,
                        total,
                        created_at
                    )
                ''') \
                .eq('user_id', user_id) \
                .eq('status', 'active') \
                .order('updated_at', desc=True) \
                .execute()
            
            if hasattr(response, 'data'):
                tabs_data = response.data
                
                # Process tab data to calculate totals and format dates
                processed_tabs = []
                for tab in tabs_data:
                    # Calculate total from orders
                    total = 0.0
                    if 'orders' in tab and tab['orders']:
                        total = sum(float(order.get('total', 0)) for order in tab['orders'])
                    
                    # Format dates
                    created_at = tab.get('created_at', '')
                    updated_at = tab.get('updated_at', '')
                    
                    if created_at:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = created_at.strftime('%b %d, %Y %I:%M %p')
                    
                    if updated_at:
                        updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        updated_at = updated_at.strftime('%b %d, %Y %I:%M %p')
                    
                    # Prepare tab data for UI
                    processed_tab = {
                        'id': tab.get('id'),
                        'tab_number': f"T-{tab.get('number', '')}" if tab.get('number') else 'N/A',
                        'status': tab.get('status', 'active'),
                        'total': total,
                        'restaurant': tab.get('restaurant', {}).get('name', 'Restaurant'),
                        'restaurant_logo': tab.get('restaurant', {}).get('logo_url', ''),
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'order_count': len(tab.get('orders', []))
                    }
                    processed_tabs.append(processed_tab)
                
                # Update UI with processed tabs
                self._update_active_tabs(processed_tabs)
            
        except Exception as e:
            logger.error(f"Error loading tabs: {e}", exc_info=True)
            self._show_error("Failed to load active tabs. Please try again later.")
            self._update_active_tabs([])
    
    @mainthread
    def _update_active_tabs(self, tabs):
        """Update the UI with the given tabs.
        
        Args:
            tabs (list): List of tab dictionaries containing tab data
        """
        self.active_tabs = tabs or []
        
        # Get reference to the tabs list container
        tabs_container = self.ids.get('active_tabs_list', None)
        if not tabs_container:
            return
        
        # Clear existing tab widgets
        tabs_container.clear_widgets()
        
        if not self.active_tabs:
            # Show empty state
            empty_label = MDLabel(
                text='No active tabs found.',
                theme_text_color='Secondary',
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(100)
            )
            tabs_container.add_widget(empty_label)
            return
        
        # Add tab cards for each tab
        for tab in self.active_tabs:
            tab_card = TabCard(
                tab_id=tab.get('id'),
                tab_number=tab.get('tab_number', 'N/A'),
                status=tab.get('status', 'active'),
                total=tab.get('total', 0.0),
                restaurant=tab.get('restaurant_name', 'Unknown')
            )
            tabs_container.add_widget(tab_card)
    
    def _start_qr_scanner(self):
        """Start the QR code scanner on Android."""
        try:
            from jnius import autoclass
            from android.permissions import request_permissions, Permission
            
            # Request camera permission
            request_permissions([Permission.CAMERA])
            
            # Start QR scanner activity
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            IntentIntegrator = autoclass('com.google.zxing.integration.android.IntentIntegrator')
            
            activity = PythonActivity.mActivity
            integrator = IntentIntegrator(activity)
            integrator.initiateScan()
            
        except Exception as e:
            logger.error(f"QR scanner error: {e}", exc_info=True)
            self._show_error("Could not start QR scanner. Please try again.")
    
    def _show_qr_input_dialog(self):
        """Show a dialog to manually enter QR code on desktop."""
        from kivymd.uix.textfield import MDTextField
        
        self.qr_input = MDTextField(
            hint_text="Enter restaurant code or scan QR",
            helper_text="Find this code on your table or receipt",
            helper_text_mode="on_focus"
        )
        
        self.dialog = MDDialog(
            title="Join a Restaurant",
            type="custom",
            content_cls=self.qr_input,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="JOIN",
                    on_release=self._on_join_restaurant,
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color
                )
            ]
        )
        self.dialog.open()
    
    def _on_join_restaurant(self, instance):
        """Handle joining a restaurant using the entered code."""
        code = self.qr_input.text.strip()
        if not code:
            self.qr_input.error = True
            self.qr_input.helper_text = "Please enter a code"
            return
            
        self.dialog.dismiss()
        self._connect_to_restaurant(code)
    
    def _connect_to_restaurant(self, code: str):
        """Connect to a restaurant using the provided code."""
        # Show loading
        self._set_loading(True, "Connecting to restaurant...")
        
        # Run in background
        asyncio.create_task(self._async_connect_to_restaurant(code))
    
    async def _async_connect_to_restaurant(self, code: str):
        """Asynchronously connect to a restaurant."""
        try:
            # Look up restaurant by code
            response = await self.auth_service.supabase.table('restaurants') \
                .select('*') \
                .eq('code', code.upper()) \
                .single() \
                .execute()
                
            if not hasattr(response, 'data') or not response.data:
                self._show_error("Restaurant not found. Please check the code and try again.")
                return
                
            restaurant = response.data
            
            # Create a new tab for this restaurant
            tab_data = {
                'restaurant_id': restaurant['id'],
                'user_id': self.auth_service.get_user_id(),
                'status': 'active',
                'total': 0.0
            }
            
            # Insert new tab
            tab_response = await self.auth_service.supabase.table('tabs') \
                .insert(tab_data) \
                .execute()
                
            if hasattr(tab_response, 'data') and tab_response.data:
                self._show_success(f"Connected to {restaurant.get('name', 'the restaurant')}")
                # Refresh tabs
                await self._load_active_tabs()
            else:
                self._show_error("Failed to create tab. Please try again.")
                
        except Exception as e:
            logger.error(f"Error connecting to restaurant: {e}", exc_info=True)
            self._show_error("Failed to connect to restaurant. Please try again.")
        finally:
            self._set_loading(False)
            
    def _load_demo_data(self):
        """Load sample data for demo mode."""
        try:
            logger.info("Loading demo data...")
            # Set demo data
            self.user_name = "Demo User"
            self.last_refresh = datetime.now().strftime("%H:%M")
            
            # Get main layout
            if not hasattr(self, 'ids') or 'main_layout' not in self.ids:
                logger.error("main_layout not found in dashboard screen")
                return
                
            main_layout = self.ids.main_layout
            
            # Clear existing content
            main_layout.clear_widgets()
            
            # Re-add app bar
            from kivymd.uix.toolbar import MDTopAppBar
            app_bar = MDTopAppBar(
                title="Billo",
                elevation=10,
                left_action_items=[['menu', lambda x: App.get_running_app().root.toggle_nav_drawer()]],
                right_action_items=[['refresh', lambda x: None], ['logout', lambda x: self.logout()]],
                md_bg_color=App.get_running_app().theme_cls.primary_color,
                specific_text_color=(1, 1, 1, 1)
            )
            main_layout.add_widget(app_bar)
            
            # Create scroll view for content
            from kivy.uix.scrollview import ScrollView
            scroll = ScrollView(do_scroll_x=False)
            
            # Create main content
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.card import MDCard
            
            content = MDBoxLayout(
                orientation='vertical',
                spacing=20,
                padding=40,
                size_hint_y=None
            )
            content.bind(minimum_height=content.setter('height'))
            
            # Add tab number
            tab_label = MDLabel(
                text="T-001",
                font_style="H1",
                halign="center",
                theme_text_color="Primary",
                size_hint_y=None,
                height=100
            )
            content.add_widget(tab_label)
            
            # Add restaurant name
            restaurant_label = MDLabel(
                text="Demo Restaurant",
                font_style="H4",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=50
            )
            content.add_widget(restaurant_label)
            
            # Add message card
            card = MDCard(
                size_hint_y=None,
                height=200,
                padding=20,
                elevation=2,
                pos_hint={'center_x': 0.5},
                size_hint_x=0.9
            )
            
            message = MDLabel(
                text="Your bills will appear here...",
                halign="center",
                valign="middle",
                theme_text_color="Secondary"
            )
            card.add_widget(message)
            content.add_widget(card)
            
            # Add content to scroll view
            scroll.add_widget(content)
            
            # Add scroll view to main layout
            main_layout.add_widget(scroll)
            
            logger.info("Demo data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading demo data: {e}", exc_info=True)
            self._show_error("Failed to load demo data")
    
    def _setup_realtime_updates(self):
        """Set up realtime subscriptions for tab and order updates."""
        try:
            # Skip realtime updates in demo mode
            app = App.get_running_app()
            if hasattr(app, 'demo_mode') and app.demo_mode:
                logger.info("Skipping realtime updates in demo mode")
                return
                
            # Get the Supabase client
            supabase = getattr(self.auth_service, 'supabase', None)
            if not supabase:
                logger.warning("Supabase client not available for realtime updates")
                return
                
            # Get current user ID - handle both auth_service methods
            user_id = None
            if hasattr(self.auth_service, 'get_user_id'):
                user_id = self.auth_service.get_user_id()
            elif hasattr(self.auth_service, 'get_current_user'):
                user = self.auth_service.get_current_user()
                user_id = user.get('id') if user else None
                
            if not user_id:
                logger.warning("No user ID available for realtime updates")
                return
                
            # Clean up any existing subscriptions
            self._cleanup_realtime_updates()
            
            logger.info("Setting up realtime updates...")
            
            # Subscribe to tab updates for this user
            self._realtime_subscription = supabase.channel('tabs')\
                .on('postgres_changes', 
                    event='*',
                    schema='public',
                    table='tabs',
                    filter=f'customer_id=eq.{user_id}',
                    callback=self._handle_realtime_update
                ).subscribe()
            
            logger.info("Realtime updates subscribed")
            
        except Exception as e:
            logger.error(f"Error setting up realtime updates: {e}", exc_info=True)
    
    def _cleanup_realtime_updates(self):
        """Clean up realtime subscriptions."""
        # Skip if in demo mode
        app = App.get_running_app()
        if hasattr(app, 'demo_mode') and app.demo_mode:
            return
        try:
            if self._realtime_subscription:
                logger.info("Cleaning up realtime subscriptions...")
                # Unsubscribe from the channel
                self._realtime_subscription.unsubscribe()
                self._realtime_subscription = None
        except Exception as e:
            logger.error(f"Error cleaning up realtime updates: {e}", exc_info=True)
    
    @mainthread
    def _handle_realtime_update(self, payload):
        """Handle realtime update from Supabase."""
        try:
            if not payload:
                return
                
            event_type = payload.get('event_type')
            record = payload.get('record', {})
            
            if not record or 'id' not in record:
                return
                
            tab_id = record['id']
            logger.info(f"Received {event_type} event for tab {tab_id}")
            
            if event_type == 'UPDATE':
                # Find and update the tab
                for i, tab in enumerate(self.active_tabs):
                    if str(tab['id']) == str(tab_id):
                        # Update tab data
                        updated_tab = {**tab}
                        
                        # Update status if changed
                        if 'status' in record:
                            updated_tab['status'] = record['status']
                            
                        # Update total if changed
                        if 'total' in record:
                            updated_tab['total'] = float(record['total'] or 0)
                            
                        # Update the tab in the list
                        self.active_tabs[i] = updated_tab
                        
                        # Show toast for order updates
                        if 'total' in record and float(record['total'] or 0) > 0:
                            tab_number = record.get('tab_number', '')
                            total = float(record['total'] or 0)
                            toast(f"Tab #{tab_number} updated: KES {total:,.2f}")
                        
                        # Update the UI
                        self._update_active_tabs(self.active_tabs)
                        break
                        
            elif event_type == 'INSERT':
                # New tab created, refresh the list
                self._load_active_tabs()
                
            elif event_type == 'DELETE':
                # Tab was closed or deleted
                self.active_tabs = [t for t in self.active_tabs if str(t['id']) != str(tab_id)]
                self._update_active_tabs(self.active_tabs)
                
        except Exception as e:
            logger.error(f"Error handling realtime update: {e}", exc_info=True)
    
    def add_new_tab(self, tab_data):
        """Add a new tab to the dashboard."""
        try:
            # Add the tab to the active tabs list if not already present
            if not any(tab.get('id') == tab_data['id'] for tab in self.active_tabs):
                # Format the tab data for display
                formatted_tab = {
                    'id': tab_data['id'],
                    'tab_number': tab_data['tab_number'],
                    'restaurant': f"Restaurant {tab_data['restaurant_id'].upper()}",
                    'status': tab_data.get('status', 'active'),
                    'total': 0.0,
                    'created_at': tab_data.get('created_at', datetime.now().isoformat()),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Add to active tabs
                self.active_tabs.append(formatted_tab)
                
                # Update the UI
                self._update_tabs_display()
                
                # Show a toast notification
                toast(f"Tab #{formatted_tab['tab_number']} created")
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error adding new tab: {e}")
            return False
    
    def _update_tabs_display(self):
        """Update the tabs display in the UI."""
        # Clear existing tab widgets
        tabs_container = self.ids.active_tabs_list
        tabs_container.clear_widgets()
        
        if not self.active_tabs:
            # Show "no tabs" message
            self.ids.no_tabs_label.opacity = 1
            return
            
        # Hide "no tabs" message
        self.ids.no_tabs_label.opacity = 0
        
        # Add tab cards for each active tab
        for tab in sorted(self.active_tabs, 
                         key=lambda x: x.get('created_at', ''), 
                         reverse=True):
            tab_card = TabCard(
                tab_id=tab['id'],
                tab_number=f"#{tab['tab_number']}",
                restaurant=tab['restaurant'],
                status=tab['status'],
                total=tab['total']
            )
            tabs_container.add_widget(tab_card)
    
    def on_connect_restaurant(self):
        """Handle connect to restaurant button press."""
        # Navigate to the restaurant connect screen
        app = App.get_running_app()
        if hasattr(app, 'sm'):
            if not app.sm.has_screen('restaurant_connect'):
                from customer_app.screens.restaurant_connect_screen import RestaurantConnectScreen
                restaurant_connect = RestaurantConnectScreen()
                app.sm.add_widget(restaurant_connect)
            app.sm.current = 'restaurant_connect'
    
    def on_scan_qr(self):
        """Handle scan QR code button press."""
        # Navigate to QR scanner screen
        if hasattr(App.get_running_app(), 'sm'):
            App.get_running_app().sm.transition = SlideTransition(direction='left')
            App.get_running_app().sm.current = 'qr_scanner'
    
    def on_view_all_tabs(self):
        """Handle view all tabs button press."""
        # TODO: Implement navigation to all tabs screen
        print("View all tabs pressed")
    
    def on_view_all_activity(self):
        """Handle view all activity button press."""
        # TODO: Navigate to activity screen
        print("View all activity")
    
    def on_settings(self):
        """Handle settings button press."""
        # TODO: Navigate to settings screen
        print("Settings")
    
    def logout(self):
        """Handle logout button press."""
        # Show confirmation dialog
        self.dialog = MDDialog(
            title="Log Out",
            text="Are you sure you want to log out?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="LOG OUT",
                    on_release=self._confirm_logout,
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color
                )
            ]
        )
        self.dialog.open()
    
    def _confirm_logout(self, instance):
        """Confirm and handle user logout."""
        if self.dialog:
            self.dialog.dismiss()
        
        # Show loading
        self._set_loading(True, "Logging out...")
        
        # Run logout in background
        asyncio.create_task(self._async_logout())
    
    async def _async_logout(self):
        """Asynchronously log out the user."""
        try:
            # Sign out through auth service
            await self.auth_service.sign_out()
            
            # Navigate to login screen on main thread
            self._navigate_to_login()
            
        except Exception as e:
            logger.error(f"Logout error: {e}", exc_info=True)
            self._show_error("Failed to log out. Please try again.")
        finally:
            self._set_loading(False)
    
    @mainthread
    def _navigate_to_login(self):
        """Navigate to the restaurant connect screen."""
        app = App.get_running_app()
        if hasattr(app, 'sm') and hasattr(app.sm, 'current'):
            app.sm.current = 'restaurant_connect'
        elif hasattr(app, 'root') and hasattr(app.root, 'current'):
            app.root.current = 'restaurant_connect'
    
    def show_error(self, message):
        """Show an error dialog."""
        # UI Helper Methods
    @mainthread
    def _set_loading(self, loading: bool, message: str = None):
        """Update loading state."""
        self.loading = loading
        
        # Show/hide loading overlay
        loading_overlay = self.ids.get('loading_overlay', None)
        if loading_overlay:
            loading_overlay.opacity = 1.0 if loading else 0.0
            
            # Update loading message if provided
            if message and hasattr(loading_overlay, 'ids'):
                loading_label = loading_overlay.ids.get('loading_label', None)
                if loading_label:
                    loading_label.text = message
    
    @mainthread
    def _show_error(self, message: str, title: str = "Error"):
        """Show an error message to the user."""
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
    
    @mainthread
    def _show_success(self, message: str, title: str = "Success"):
        """Show a success message to the user."""
        toast(message)
    
    @mainthread
    @mainthread
    def _update_recent_activity(self, activities):
        """Update the UI with recent activities.
        
        Args:
            activities (list): List of activity dictionaries
        """
        self.recent_activity = activities or []
        
        # Get reference to the activity list container
        activity_container = self.ids.get('recent_activity_list', None)
        if not activity_container:
            return
            
        # Clear existing activity widgets
        activity_container.clear_widgets()
        
        if not self.recent_activity:
            # Show empty state
            empty_label = MDLabel(
                text='No recent activity.',
                theme_text_color='Secondary',
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(100)
            )
            activity_container.add_widget(empty_label)
            return
            
        # Add activity items
        for activity in self.recent_activity:
            # Create activity card
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(100),
                padding=dp(10),
                spacing=dp(5),
                elevation=1,
                radius=[10,],
                ripple_behavior=True
            )
            
            # Add content to card
            box = BoxLayout(orientation='horizontal', spacing=dp(10))
            
            # Left side - Icon
            icon = MDIcon(
                icon='receipt' if activity.get('type') == 'order' else 'update',
                size_hint_x=0.15,
                theme_text_color='Primary'
            )
            
            # Middle - Details
            details = BoxLayout(orientation='vertical', spacing=dp(2))
            
            # Status and time
            status_row = BoxLayout(size_hint_y=None, height=dp(20))
            status_chip = MDChip(
                text=activity.get('status', '').upper(),
                size_hint=(None, None),
                size=(dp(80), dp(20)),
                font_size='10sp',
                theme_text_color='Custom',
                text_color=(1, 1, 1, 1)
            )
            
            # Set chip color based on status
            status = activity.get('status', '').lower()
            if status == 'completed':
                status_chip.md_bg_color = [0.3, 0.69, 0.31, 1.0]  # Green 600
            elif status == 'pending':
                status_chip.md_bg_color = [1.0, 0.6, 0.0, 1.0]  # Orange 500
            else:
                status_chip.md_bg_color = [0.62, 0.62, 0.62, 1.0]  # Grey 400
                
            status_row.add_widget(status_chip)
            
            # Add time
            time_label = MDLabel(
                text=activity.get('created_at', ''),
                theme_text_color='Secondary',
                font_style='Caption',
                halign='right',
                size_hint_x=0.6
            )
            status_row.add_widget(time_label)
            
            details.add_widget(status_row)
            
            # Tab info
            tab_info = MDLabel(
                text=f"Tab #{activity.get('tab_number', '')} • {activity.get('restaurant', 'Restaurant')}",
                theme_text_color='Primary',
                font_style='Subtitle2',
                size_hint_y=None,
                height=dp(20)
            )
            details.add_widget(tab_info)
            
            # Items
            items_label = MDLabel(
                text=", ".join(activity.get('items', [])[:3]),
                theme_text_color='Secondary',
                font_style='Caption',
                size_hint_y=None,
                height=dp(16),
                halign='left',
                max_lines=1,
                shorten=True,
                shorten_from='right',
                text_size=('200dp', None)
            )
            details.add_widget(items_label)
            
            # Total
            total_label = MDLabel(
                text=f"${float(activity.get('total', 0)):.2f}",
                theme_text_color='Primary',
                font_style='Subtitle1',
                halign='left',
                bold=True
            )
            details.add_widget(total_label)
            
            # Add widgets to card
            box.add_widget(icon)
            box.add_widget(details)
            card.add_widget(box)
            
            # Add click handler
            card.bind(on_release=lambda x, a=activity: self._on_activity_clicked(a))
            
            # Add card to container
            activity_container.add_widget(card)
    
    def _on_activity_clicked(self, activity):
        """Handle click on activity item."""
        # TODO: Navigate to order/tab details
        tab_id = activity.get('tab_id')
        print(f"Activity clicked for tab {tab_id}")
