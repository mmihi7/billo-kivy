import os
import sys
import platform
import asyncio
import logging
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.clock import Clock, mainthread
from kivymd.app import MDApp

# Import Supabase client
from supabase import create_client, Client as SupabaseClient

# Import services
from shared.auth_service import AuthService

# Import screens
from customer_app.screens.auth.login_screen import LoginScreen
from customer_app.screens.auth.register_screen import RegisterScreen
from customer_app.screens.dashboard_screen import DashboardScreen
from customer_app.screens.qr_scanner_screen import QRScannerScreen
from customer_app.screens.restaurant_connect_screen import RestaurantConnectScreen

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BilloCustomerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Billo - Customer"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        # Initialize app state
        self.demo_mode = False
        self.supabase = None
        self.auth_service = None
        self.sm = None
        self.screens = {}
        
        # Initialize platform-specific settings
        self._init_platform()
        
    def _init_platform(self):
        """Initialize platform-specific settings."""
        if platform == 'android':
            from jnius import autoclass
            self._activity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # Set up broadcast receiver for deep links
            Intent = autoclass('android.content.Intent')
            IntentFilter = autoclass('android.content.IntentFilter')
            self._broadcast_receiver = autoclass('com.example.billo.BroadcastReceiver')()
            
            # Register the receiver
            filter = IntentFilter()
            filter.addAction(Intent.ACTION_VIEW)
            filter.addDataScheme('billo')
            self._activity.registerReceiver(self._broadcast_receiver, filter)
    
    def initialize_services(self):
        """Initialize all required services."""
        if self.demo_mode:
            logger.info("Skipping service initialization in demo mode")
            return True
            
        try:
            logger.info("Initializing Supabase client...")
            from supabase import create_client
            import os
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                logger.error("Missing Supabase URL or Key in environment variables")
                return False
                
            self.supabase = create_client(supabase_url, supabase_key)
            
            # Only initialize auth service if not in demo mode
            if not self.demo_mode:
                logger.info("Initializing AuthService...")
                self.auth_service = AuthService(self.supabase)
                self.auth_service.add_auth_listener(self.on_auth_state_changed)
            
            logger.info("Services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def build(self):
        """Build the Kivy application."""
        logger.info("Building application...")
        
        # Initialize the screen manager with no transition
        self.sm = ScreenManager(transition=NoTransition())
        
        # Initialize demo screens
        self._init_screens()
        
        # Add demo screens to screen manager
        for name, screen in self.screens.items():
            self.sm.add_widget(screen)
            logger.info(f"Added screen: {name}")
        
        # Start with restaurant connect screen
        self.sm.current = 'restaurant_connect'
        logger.info("Demo mode started with restaurant connect screen")
        
        return self.sm
        
    def _set_initial_screen(self, dt):
        """Set the initial screen to restaurant_connect."""
        if hasattr(self, 'sm') and hasattr(self.sm, 'current'):
            logger.info("Setting initial screen to restaurant_connect")
            self.sm.current = 'restaurant_connect'
            logger.info(f"Current screen is now: {self.sm.current}")
            return False
        logger.warning("Screen manager not properly initialized")
        return True
        
    def _init_screens(self):
        """Initialize demo screens."""
        try:
            logger.info("Initializing demo screens...")
            
            # Import demo screens
            from customer_app.screens.restaurant_connect_screen import RestaurantConnectScreen
            from customer_app.screens.demo_login_screen import DemoLoginScreen
            from customer_app.screens.demo_dashboard_screen import DemoDashboardScreen
            
            # Initialize demo screens
            self.screens = {
                'restaurant_connect': RestaurantConnectScreen(name='restaurant_connect'),
                'demo_login': DemoLoginScreen(name='demo_login'),
                'demo_dashboard': DemoDashboardScreen(name='demo_dashboard')
            }
            
            # Set demo mode
            self.demo_mode = True
            logger.info("Demo mode initialized with login and dashboard screens")
                    
            logger.info(f"Initialized {len(self.screens)} screens")
            
        except Exception as e:
            logger.error(f"Failed to initialize screens: {e}")
            import traceback
            traceback.print_exc()
    
    @mainthread
    def on_auth_state_changed(self, user):
        """Handle authentication state changes."""
        try:
            if user:
                logger.info(f"User authenticated: {user.get('email', 'Unknown')}")
                # Don't change screens, stay on current screen
                pass
            else:
                logger.info("User signed out")
                # Switch to restaurant connect screen
                self.switch_screen('restaurant_connect')
        except Exception as e:
            logger.error(f"Error in auth state change: {e}")
            import traceback
            traceback.print_exc()
    
    @mainthread
    def switch_screen(self, screen_name, direction='left'):
        """Switch to a different screen with a transition."""
        try:
            if not hasattr(self, 'sm') or not hasattr(self.sm, 'current'):
                logger.error("Screen manager not properly initialized")
                return
                
            if screen_name not in self.sm.screen_names:
                logger.error(f"Screen {screen_name} not found in screen manager")
                return
                
            # Save current transition
            current_transition = self.sm.transition
            
            # If switching to restaurant_connect, use NoTransition
            if screen_name == 'restaurant_connect':
                self.sm.transition = NoTransition()
            else:
                # Set transition based on direction
                if direction == 'left':
                    self.sm.transition.direction = 'left'
                elif direction == 'right':
                    self.sm.transition.direction = 'right'
                elif direction == 'up':
                    self.sm.transition.direction = 'up'
                elif direction == 'down':
                    self.sm.transition.direction = 'down'
                
            self.sm.current = screen_name
            logger.info(f"Switched to screen: {screen_name}")
            
            # Restore original transition
            self.sm.transition = current_transition
            
        except Exception as e:
            logger.error(f"Error switching to screen {screen_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def on_start(self):
        """Called when the application starts."""
        try:
            # Set window size for development
            if platform == 'win32' or platform == 'darwin':
                Window.size = (400, 700)
                Window.top = 100
                Window.left = 100
                
            logger.info("Application started")
            
        except Exception as e:
            logger.error(f"Error in on_start: {e}")
            import traceback
            traceback.print_exc()
    
    def on_stop(self):
        """Called when the application is closing."""
        try:
            # Clean up resources
            if hasattr(self, '_broadcast_receiver'):
                try:
                    activity = self._activity
                    activity.unregisterReceiver(self._broadcast_receiver)
                except Exception as e:
                    logger.warning(f"Error unregistering receiver: {e}")
                    
            logger.info("Application stopping...")
            
        except Exception as e:
            logger.error(f"Error in on_stop: {e}")
            import traceback
            traceback.print_exc()
            
        return super().on_stop()


def main():
    """Main entry point for the application."""
    try:
        logger.info("Starting Billo Customer App...")
        app = BilloCustomerApp()
        return app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    main()
    
    update_ui()
    
    def initialize_supabase(self) -> SupabaseClient:
        """Initialize and return the Supabase client."""
        try:
            print("Initializing Supabase client...")
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            print(f"Supabase URL: {'Found' if supabase_url else 'Missing'}")
            print(f"Supabase Key: {'Found' if supabase_key else 'Missing'}")
            
            if not supabase_url or not supabase_key:
                error_msg = "Missing Supabase URL or API key in environment variables"
                print(error_msg)
                raise ValueError(error_msg)
                
            client = create_client(supabase_url, supabase_key)
            print("Supabase client initialized successfully")
            return client
            
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            import traceback
            traceback.print_exc()
            raise

    @mainthread
    def on_auth_state_changed(self, user):
        """Handle authentication state changes."""
        try:
            if user:
                logger.info(f"User authenticated: {user.get('email', 'Unknown')}")
                # Don't change screens, stay on current screen
                pass
            else:
                logger.info("User signed out")
                # Switch to restaurant connect screen
                self.switch_screen('restaurant_connect')
        except Exception as e:
            logger.error(f"Error in auth state change: {e}")
            import traceback
            traceback.print_exc()

@mainthread
def switch_screen(self, screen_name, direction='left'):
    """Switch to a different screen."""
    try:
        if not hasattr(self, 'sm') or not self.sm:
            logger.error("Screen manager not initialized")
            return
            
        if not screen_name in self.sm.screen_names:
            logger.error(f"Screen {screen_name} not found in screen manager")
            return
            
        logger.info(f"Switching to screen: {screen_name}")
        self.sm.transition.direction = direction
        self.sm.current = screen_name
        
    except Exception as e:
        logger.error(f"Error switching to screen {screen_name}: {e}")
        import traceback
        traceback.print_exc()

def on_start(self):
    """Called when the application starts."""
    try:
        # Set window size for development
        if platform == 'win32' or platform == 'darwin':
            Window.size = (400, 700)
            Window.top = 100
            Window.left = 100
            
        logger.info("Application started")
        
    except Exception as e:
        logger.error(f"Error in on_start: {e}")
        import traceback
        traceback.print_exc()

def on_stop(self):
    """Called when the application is closing."""
    try:
        # Clean up resources
        if hasattr(self, '_broadcast_receiver'):
            try:
                activity = self._activity
                activity.unregisterReceiver(self._broadcast_receiver)
            except Exception as e:
                logger.warning(f"Error unregistering receiver: {e}")
                
        logger.info("Application stopping...")
        
    except Exception as e:
        logger.error(f"Error in on_stop: {e}")
        import traceback
        traceback.print_exc()
        
    return super().on_stop()

def initialize_supabase(self) -> SupabaseClient:
    """Initialize and return the Supabase client."""
    try:
        print("Initializing Supabase client...")
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        print(f"Supabase URL: {'Found' if supabase_url else 'Missing'}")
        print(f"Supabase Key: {'Found' if supabase_key else 'Missing'}")
        
        if not supabase_url or not supabase_key:
            error_msg = "Missing Supabase URL or API key in environment variables"
            print(error_msg)
            raise ValueError(error_msg)
            
        client = create_client(supabase_url, supabase_key)
        print("Supabase client initialized successfully")
        return client
        
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        import traceback
        traceback.print_exc()
        raise

def initialize_screens(self):
    """Initialize all screens for the application."""
    print(f"[DEBUG] initialize_screens - auth_service: {self.auth_service}")
    if not self.auth_service:
        print("[ERROR] auth_service is None during screen initialization!")
        
    # Initialize screens with auth service
    print("[DEBUG] Creating login screen...")
    login_screen = LoginScreen(auth_service=self.auth_service)
    print("[DEBUG] Creating register screen...")
    register_screen = RegisterScreen(auth_service=self.auth_service)
    print("[DEBUG] Creating dashboard screen...")
    dashboard_screen = DashboardScreen(auth_service=self.auth_service)
    print("[DEBUG] Creating QR scanner screen...")
    qr_scanner = QRScannerScreen()
    print("[DEBUG] Creating restaurant connect screen...")
    restaurant_connect = RestaurantConnectScreen()
    
    self.screens = {
        'login': login_screen,
        'register': register_screen,
        'dashboard': dashboard_screen,
        'qr_scanner': qr_scanner,
        'restaurant_connect': restaurant_connect
    }
    
    # Add screens to manager
    for name, screen in self.screens.items():
        screen.name = name
        self.sm.add_widget(screen)
        
    # Always start with restaurant connect screen
    self.sm.transition = NoTransition()
    self.sm.current = 'restaurant_connect'

@mainthread
def on_auth_state_changed(self, user):
    """Handle authentication state changes."""
    try:
        if user:
            print(f"User authenticated: {user.email}")
            # Don't change screens, just update the UI as needed
            pass
        else:
            print("User signed out")
            # Don't change screens, stay on the current screen
            pass
    except Exception as e:
        print(f"Error in auth state change: {e}")
        import traceback
        traceback.print_exc()

@mainthread
def switch_screen(self, screen_name, direction='left', **kwargs):
    """Switch to a different screen with a transition."""
    try:
        if not hasattr(self, 'sm') or not self.sm:
            print("Screen manager not initialized")
            return
            
        # Handle special case for QR scanner with demo mode
        if screen_name == 'qr_scanner' and kwargs.get('demo_mode', False):
            # Create a new instance of QRScannerScreen with demo_mode=True
            from customer_app.screens.qr_scanner_screen import QRScannerScreen
            qr_screen = QRScannerScreen(demo_mode=True, name='qr_scanner')
            
            # Remove existing qr_scanner screen if it exists
            if 'qr_scanner' in self.sm.screen_names:
                self.sm.remove_widget(self.sm.get_screen('qr_scanner'))
                
            self.sm.add_widget(qr_screen)
            self.screens['qr_scanner'] = qr_screen
        
        if not screen_name in self.sm.screen_names:
            print(f"Screen {screen_name} not found in screen manager")
            return
            
        print(f"Switching to screen: {screen_name}")
        self.sm.transition.direction = direction
        self.sm.current = screen_name
        print(f"Current screen is now: {self.sm.current}")
    except Exception as e:
        print(f"Error switching to screen {screen_name}: {e}")
        import traceback
        traceback.print_exc()

def load_kv_files(self):
    """Load all KV files."""
    kv_files = [
        'customer_app/screens/auth/login_screen.kv',
        'customer_app/screens/auth/register_screen.kv',
        'customer_app/screens/dashboard_screen.kv',
        'customer_app/screens/qr_scanner_screen.kv',
        'customer_app/screens/restaurant_connect_screen.kv'
    ]
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    loaded_files = set()
    
    for kv_file in kv_files:
        try:
            full_path = os.path.join(base_dir, kv_file)
            if full_path in loaded_files:
                continue
                
            if os.path.exists(full_path):
                Builder.load_file(full_path)
                loaded_files.add(full_path)
                print(f"Successfully loaded KV file: {kv_file}")
            else:
                print(f"KV file not found: {full_path}")
        except Exception as e:
            if 'is loaded multiples times' not in str(e):
                print(f"Error loading {kv_file}: {e}")

def _on_new_intent(self, context, intent):
    """Handle new intents (deep links)."""
    from jnius import autoclass
    
    try:
        # Get the intent data
        Intent = autoclass('android.content.Intent')
        
        # Get the data from the intent
        data = intent.getData()
        if data:
            # Handle the OAuth callback
            asyncio.create_task(
                self.auth_service.handle_oauth_callback(str(data.toString()))
            )
    except Exception as e:
        print(f"Error handling intent: {e}")

def _init_async(self):
    """Initialize async components."""
    async def initialize():
        # Any async initialization can go here
        if hasattr(self, 'auth_service') and self.auth_service:
            try:
                await self.auth_service.initialize()
                self.auth_service.add_auth_listener(self.on_auth_state_changed)
            except Exception as e:
                print(f"[ERROR] Error in async initialization: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize())

def build(self):
    """Build the application."""
    # Initialize screen manager
    self.sm = ScreenManager()
    
    # Initialize services
    if not hasattr(self, 'auth_service') or not self.auth_service:
        from shared.auth_service import AuthService
        self.auth_service = AuthService()
    
    # Load KV files first
    self.load_kv_files()
    
    # Initialize screens
    self.initialize_screens()
    
    # Set initial screen based on auth state
    # Always start with restaurant connect screen
    self.sm.current = 'restaurant_connect'
    
    # Schedule async initialization after the app starts
    Clock.schedule_once(lambda dt: self._init_async(), 0)
    
    return self.sm

def handle_deep_link(self, url):
    """Handle deep links (e.g., OAuth callbacks)."""
    if hasattr(self, 'auth_service') and self.auth_service and 'login-callback' in url:
        asyncio.create_task(self.auth_service.handle_oauth_callback(url))

def main():
    """Main entry point for the application."""
    app = BilloCustomerApp()
    return app.run()

if __name__ == '__main__':
    main()
