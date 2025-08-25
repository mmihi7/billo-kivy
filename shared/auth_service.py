from typing import Optional, Dict, Any, Tuple
from supabase import Client as SupabaseClient
from gotrue import User, AuthResponse
import logging
from kivy.app import App
from kivy.clock import mainthread
import webbrowser
import json

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self._current_user: Optional[User] = None
        self._auth_listeners = []
        self._deep_link_handlers = {}
        
        # Register deep link handler for OAuth callbacks
        from kivy.core.window import Window
        Window.bind(on_keyboard=self._handle_key_event)

    @property
    def current_user(self) -> Optional[User]:
        """Get the currently authenticated user."""
        if not self._current_user:
            try:
                self._current_user = self.supabase.auth.get_user()
            except Exception as e:
                logger.warning(f"Error getting current user: {e}")
                return None
        return self._current_user

    def _handle_key_event(self, instance, key, *args):
        """Handle deep links for OAuth callbacks."""
        if key == 'app_handled_back' and hasattr(self, '_deeplink_url'):
            for handler in self._deep_link_handlers.values():
                handler(self._deeplink_url)
            self._deeplink_url = None
            return True
        return False

    def handle_deep_link(self, url: str):
        """Handle deep link for OAuth callbacks."""
        if 'access_token=' in url and 'refresh_token=' in url:
            self._deeplink_url = url
            return True
        return False

    def add_auth_listener(self, callback):
        """Add a callback for auth state changes."""
        self._auth_listeners.append(callback)
        return lambda: self._auth_listeners.remove(callback)

    def _notify_auth_listeners(self):
        """Notify all auth state change listeners."""
        for callback in self._auth_listeners:
            try:
                callback(self._current_user)
            except Exception as e:
                logger.error(f"Error in auth listener: {e}")

    @mainthread
    def _on_auth_state_change(self, event, session):
        """Handle auth state changes from Supabase."""
        if event == 'TOKEN_REFRESHED' or event == 'SIGNED_IN':
            self._current_user = session.user
            self._notify_auth_listeners()
        elif event == 'SIGNED_OUT':
            self._current_user = None
            self._notify_auth_listeners()

    async def initialize(self):
        """Initialize the auth service and set up listeners."""
        try:
            # Set up auth state change listener
            self.supabase.auth.on_auth_state_change(self._on_auth_state_change)
            
            # Try to restore session
            try:
                session = self.supabase.auth.get_session()
                if session:
                    self._current_user = session.user
            except Exception as e:
                logger.warning(f"Failed to restore session: {e}")
                
        except Exception as e:
            logger.error(f"Auth initialization error: {e}")

    async def sign_up(self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None) -> User:
        """Sign up a new user with email and password."""
        print(f"[AUTH] Starting sign up for: {email}")
        try:
            sign_up_data = {
                'email': email,
                'password': password,
                'options': {
                    'data': user_metadata or {}
                }
            }
            print(f"[AUTH] Sign up data: {sign_up_data}")
            
            response = await self.supabase.auth.sign_up(sign_up_data)
            print(f"[AUTH] Supabase sign up response: {response}")
            
            if not response or not hasattr(response, 'user'):
                error_msg = "No user in response from Supabase"
                print(f"[AUTH] {error_msg}")
                raise Exception(error_msg)
                
            self._current_user = response.user
            print(f"[AUTH] User created with ID: {response.user.id}")
            
            # Notify listeners on the main thread
            if hasattr(self, '_notify_auth_listeners'):
                self._notify_auth_listeners()
            else:
                print("[AUTH] Warning: _notify_auth_listeners not available")
                
            return response.user
            
        except Exception as e:
            error_msg = f"Sign up error: {str(e)}"
            print(f"[AUTH] {error_msg}")
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e

    async def sign_in(self, email: str, password: str) -> User:
        """Sign in a user with email and password."""
        try:
            response = await self.supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            self._current_user = response.user
            self._notify_auth_listeners()
            return response.user
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            raise
            
    async def sign_in_with_google(self):
        """Initiate Google OAuth sign-in."""
        try:
            # Generate a random state token for CSRF protection
            import secrets
            state = secrets.token_urlsafe(16)
            
            # Store the state token for verification
            app = App.get_running_app()
            app.state_token = state
            
            # Get the OAuth URL from Supabase
            response = await self.supabase.auth.sign_in_with_oauth({
                'provider': 'google',
                'options': {
                    'redirect_to': 'com.billo.pos://login-callback',
                    'query_params': {
                        'access_type': 'offline',
                        'prompt': 'select_account',
                        'state': state
                    }
                }
            })
            
            # Open the URL in the default browser
            if hasattr(response, 'url'):
                webbrowser.open(response.url)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Google sign in error: {e}")
            raise
            
    async def handle_oauth_callback(self, url: str) -> bool:
        """Handle OAuth callback URL."""
        try:
            # Parse the URL to extract the code and state
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # Verify state to prevent CSRF
            app = App.get_running_app()
            if 'state' not in params or params['state'][0] != getattr(app, 'state_token', ''):
                logger.error("Invalid state token in OAuth callback")
                return False
                
            # Exchange the code for a session
            if 'code' in params:
                await self.supabase.auth.exchange_code_for_session(params['code'][0])
                return True
                
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            
        return False

    async def sign_out(self) -> None:
        """Sign out the current user."""
        try:
            await self.supabase.auth.sign_out()
            self._current_user = None
            self._notify_auth_listeners()
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            raise

    async def reset_password(self, email: str) -> None:
        """Send a password reset email."""
        try:
            await self.supabase.auth.reset_password_email(email)
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            raise

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        if not self.current_user:
            return False
            
        # Check if the session is still valid
        try:
            session = self.supabase.auth.get_session()
            return session is not None and session.expires_at > time.time()
        except:
            return False

    async def update_profile(self, **kwargs) -> User:
        """Update the current user's profile."""
        if not self.current_user:
            raise ValueError("No user is currently signed in")
        
        try:
            response = await self.supabase.auth.update_user({
                'data': kwargs
            })
            self._current_user = response.user
            self._notify_auth_listeners()
            return response.user
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            raise
            
    def get_user_metadata(self) -> dict:
        """Get the current user's metadata."""
        if not self.current_user:
            return {}
            
        metadata = {}
        if hasattr(self.current_user, 'user_metadata'):
            metadata.update(self.current_user.user_metadata or {})
        if hasattr(self.current_user, 'app_metadata'):
            metadata.update(self.current_user.app_metadata or {})
            
        return metadata
