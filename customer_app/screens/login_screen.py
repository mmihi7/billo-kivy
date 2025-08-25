from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from shared.supabase_client import supabase
from shared.utils import Utils

class LoginScreen(Screen):
    """Login screen for customer authentication."""
    
    email = StringProperty("")
    password = StringProperty("")
    loading = BooleanProperty(False)
    error_message = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
    
    def on_pre_enter(self):
        """Called before the screen is displayed."""
        # Reset form
        self.email = ""
        self.password = ""
        self.error_message = ""
    
    def show_error_dialog(self, message):
        """Show an error dialog with the given message."""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def validate_form(self):
        """Validate the login form."""
        if not self.email or "@" not in self.email:
            self.error_message = "Please enter a valid email address"
            return False
        
        if not self.password or len(self.password) < 6:
            self.error_message = "Password must be at least 6 characters"
            return False
            
        self.error_message = ""
        return True
    
    def on_login_success(self, *args):
        """Handle successful login."""
        self.loading = False
        self.manager.current = 'dashboard'
    
    def on_login_failure(self, error):
        """Handle login failure."""
        self.loading = False
        error_message = str(error)
        
        # Parse error message to be more user-friendly
        if "Invalid login credentials" in error_message:
            error_message = "Invalid email or password"
        elif "Email not confirmed" in error_message:
            error_message = "Please confirm your email before logging in"
        
        self.show_error_dialog(error_message)
    
    def login(self):
        """Handle login button press."""
        if not self.validate_form():
            return
        
        self.loading = True
        
        try:
            # Sign in with Supabase
            result = supabase.client.auth.sign_in_with_password({
                "email": self.email,
                "password": self.password
            })
            
            # Schedule the success callback on the next frame
            Clock.schedule_once(self.on_login_success, 0.1)
            
        except Exception as e:
            self.on_login_failure(e)
    
    def navigate_to_register(self):
        """Navigate to the registration screen."""
        # TODO: Implement registration screen navigation
        pass
    
    def reset_password(self):
        """Handle password reset request."""
        if not self.email or "@" not in self.email:
            self.error_message = "Please enter your email to reset password"
            return
        
        try:
            # Send password reset email
            supabase.client.auth.reset_password_email(self.email)
            self.show_error_dialog("Password reset email sent. Please check your inbox.")
        except Exception as e:
            self.show_error_dialog(f"Failed to send reset email: {str(e)}")
