import asyncio
import logging
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import mainthread
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.textfield import MDTextField

# Set up logging
logger = logging.getLogger(__name__)

# KV file is loaded separately in app.py

class LoginScreen(Screen):
    dialog = None
    loading = False
    error_message = ""
    email = ""
    password = ""
    is_demo_mode = False
    
    def __init__(self, auth_service=None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service
        self.loading = False
        self.error_message = ""
        self.email = ""
        self.password = ""
        self.is_demo_mode = False
    
    def try_login(self, *args):
        """Attempt to log in the user."""
        email = self.ids.email_field.text.strip()
        password = self.ids.password_field.text
        
        if not email or not password:
            self.show_error("Please fill in all fields")
            return
        
        # Check for demo credentials
        if email == 'demo@example.com' and password == 'demo123':
            self.is_demo_mode = True
            self.on_demo_login()
            return
            
        # Show loading indicator for regular login
        self.show_loading("Signing in...")
        self.is_demo_mode = False
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Schedule the coroutine to run in the event loop
        if loop.is_running():
            loop.create_task(self._async_try_login(email, password))
        else:
            loop.run_until_complete(self._async_try_login(email, password))
    
    async def _async_try_login(self, email: str, password: str):
        """Handle the async login process."""
        try:
            user = await self.auth_service.sign_in(email, password)
            return user, None
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return None, str(e)
    
    def _handle_login_result(self, future):
        """Handle the result of the login attempt."""
        try:
            user, error = future.result()
            if error:
                self.show_error(error)
            else:
                self.on_login_success(user)
        except Exception as e:
            logger.error(f"Error handling login result: {e}", exc_info=True)
            self.show_error("An unexpected error occurred")
        finally:
            self.dismiss_loading()
    
    @mainthread
    def on_login_success(self, user):
        """Handle successful login."""
        if self.is_demo_mode:
            logger.info("Demo user logged in")
            # Set demo mode in the app instance
            app = App.get_running_app()
            app.demo_mode = True
            # Navigate to dashboard
            if hasattr(app, 'sm') and hasattr(app.sm, 'current'):
                app.sm.current = 'dashboard'
        else:
            logger.info(f"User logged in: {user.email}")
        
        self.dismiss_loading()
    
    def on_demo_login(self):
        """Handle demo login without actual authentication."""
        # Create a mock user object
        from types import SimpleNamespace
        demo_user = SimpleNamespace(email='demo@example.com', id='demo-user-123')
        self.on_login_success(demo_user)
    
    @mainthread
    def show_loading(self, message="Loading..."):
        """Show a loading dialog."""
        self.loading = True
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title=message,
            type="custom",
            auto_dismiss=False,
            buttons=[],
            content_cls=MDBoxLayout(
                MDSpinner(
                    size_hint=(None, None),
                    size=(dp(46), dp(46)),
                    pos_hint={'center_x': 0.5},
                    active=True
                ),
                orientation='vertical',
                spacing=12,
                padding=10,
                size_hint=(None, None),
                size=(300, 100)
            )
        )
        self.dialog.open()
        
    def dismiss_loading(self):
        """Dismiss the loading dialog."""
        self.loading = False
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    
    @mainthread
    def show_error(self, message, title="Error"):
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
    
    def switch_to_register(self):
        """Switch to the registration screen."""
        app = App.get_running_app()
        app.switch_screen('register')
    
    def navigate_to_register(self):
        """Alias for switch_to_register for backward compatibility."""
        self.switch_to_register()
    
    def show_reset_dialog(self):
        """Show the password reset dialog."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        
        self.reset_dialog = MDDialog(
            title="Reset Password",
            type="custom",
            content_cls=MDTextField(
                hint_text="Enter your email address",
                helper_text="We'll send you a password reset link",
                helper_text_mode="on_error",
                required=True,
                id="reset_email"
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.reset_dialog.dismiss()
                ),
                MDFlatButton(
                    text="SEND LINK",
                    on_release=self._on_reset_password_confirm
                )
            ]
        )
        self.reset_dialog.open()
    
    def _on_reset_password_confirm(self, instance):
        """Handle password reset confirmation."""
        email_input = self.reset_dialog.content_cls
        email = email_input.text.strip()
        
        if not email:
            email_input.error = True
            email_input.helper_text = "Email is required"
            return
        
        # Show loading
        self.reset_dialog.dismiss()
        self.show_loading("Sending reset link...")
        
        # Trigger password reset
        asyncio.create_task(self._async_reset_password(email))
    
    async def _async_reset_password(self, email: str):
        """Handle async password reset."""
        try:
            await self.auth_service.reset_password(email)
            self.show_success(
                "Password Reset Email Sent",
                "Check your email for a link to reset your password."
            )
        except Exception as e:
            logger.error(f"Password reset error: {e}", exc_info=True)
            self.show_error(
                "Failed to send reset email. Please try again.",
                "Error"
            )
        finally:
            self.dismiss_loading()
    
    def show_success(self, title: str, message: str):
        """Show a success message to the user."""
        self.show_error(message, title)
        from kivymd.uix.textfield import MDTextField
        
        self.reset_email = MDTextField(
            hint_text="Enter your email",
            helper_text="We'll send you a password reset link",
            helper_text_mode="on_error"
        )
        
        self.dialog = MDDialog(
            title="Reset Password",
            type="custom",
            content_cls=self.reset_email,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="SEND",
                    on_release=self.send_reset_email
                )
            ]
        )
        self.dialog.open()
    
    def send_reset_email(self, *args):
        """Send a password reset email."""
        email = self.reset_email.text.strip()
        if not email:
            self.reset_email.error = True
            self.reset_email.helper_text = "Email is required"
            return
            
        try:
            # TODO: Call auth service reset password
            print(f"Sending reset email to {email}")
            self.dialog.dismiss()
            self.show_success("Password reset email sent!")
        except Exception as e:
            self.show_error(str(e))
