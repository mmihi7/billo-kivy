import asyncio
import re
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

# Set up logging
logger = logging.getLogger(__name__)

# Email validation regex
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

Builder.load_string('''
<RegisterScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint: 0.8, 0.9

        MDLabel:
            text: 'Create Account'
            font_style: 'H4'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: name
            hint_text: 'Full Name'
            helper_text: 'Enter your full name'
            helper_text_mode: 'on_error'
            required: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}

        MDTextField:
            id: email
            hint_text: 'Email'
            helper_text: 'Enter your email address'
            helper_text_mode: 'on_error'
            required: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}

        MDTextField:
            id: phone
            hint_text: 'Phone Number'
            helper_text: 'Enter your phone number'
            helper_text_mode: 'on_error'
            required: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}

        MDTextField:
            id: password
            hint_text: 'Password'
            helper_text: 'At least 8 characters'
            helper_text_mode: 'on_error'
            password: True
            required: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}

        MDTextField:
            id: confirm_password
            hint_text: 'Confirm Password'
            helper_text: 'Passwords must match'
            helper_text_mode: 'on_error'
            password: True
            required: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}

        MDRaisedButton:
            text: 'Create Account'
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}
            on_release: root.try_register()

        MDTextButton:
            text: 'Already have an account? Sign In'
            theme_text_color: 'Primary'
            on_release: root.switch_to_login()
''')

class RegisterScreen(Screen):
    dialog = None
    
    def __init__(self, auth_service=None, **kwargs):
        super().__init__(**kwargs)
        print(f"[DEBUG] RegisterScreen.__init__ - auth_service: {auth_service}")
        self.auth_service = auth_service
        print(f"[DEBUG] RegisterScreen - self.auth_service set to: {self.auth_service}")
        if not self.auth_service:
            print("[ERROR] RegisterScreen initialized without auth_service!")
    
    def validate_form(self):
        """Validate the registration form."""
        # Reset errors
        for field_id in ['name', 'email', 'phone', 'password', 'confirm_password']:
            field = self.ids.get(field_id)
            if field:
                field.error = False
                field.helper_text = ""
        
        # Check required fields
        name = self.ids.name.text.strip()
        email = self.ids.email.text.strip().lower()
        phone = self.ids.phone.text.strip()
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text
        
        # Validate name
        if not name:
            self.ids.name.error = True
            self.ids.name.helper_text = "Name is required"
            return False
            
        # Validate email
        if not email:
            self.ids.email.error = True
            self.ids.email.helper_text = "Email is required"
            return False
            
        if not re.match(EMAIL_REGEX, email):
            self.ids.email.error = True
            self.ids.email.helper_text = "Please enter a valid email address"
            return False
            
        # Validate phone (basic validation)
        if not phone:
            self.ids.phone.error = True
            self.ids.phone.helper_text = "Phone number is required"
            return False
            
        # Validate password
        if not password:
            self.ids.password.error = True
            self.ids.password.helper_text = "Password is required"
            return False
            
        if len(password) < 8:
            self.ids.password.error = True
            self.ids.password.helper_text = "Password must be at least 8 characters"
            return False
            
        # Validate password confirmation
        if password != confirm_password:
            self.ids.confirm_password.error = True
            self.ids.confirm_password.helper_text = "Passwords do not match"
            return False
            
        return True
        
        # Validate email format
        if '@' not in fields['email'].text:
            fields['email'].error = True
            fields['email'].helper_text = "Invalid email format"
            return False
        
        # Validate password match
        if fields['password'].text != fields['confirm_password'].text:
            fields['confirm_password'].error = True
            fields['confirm_password'].helper_text = "Passwords don't match"
            return False
        
        # Validate password length
        if len(fields['password'].text) < 8:
            fields['password'].error = True
    
    def try_register(self):
        """Attempt to register the user."""
        if not self.validate_form():
            return
            
        # Show loading indicator
        self.show_loading("Creating your account...")
        
        # Get form data
        name = self.ids.name.text.strip()
        email = self.ids.email.text.strip().lower()
        phone = self.ids.phone.text.strip()
        password = self.ids.password.text
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Schedule the coroutine to run in the event loop
        if loop.is_running():
            loop.create_task(self._async_register_user(name, email, phone, password))
        else:
            loop.run_until_complete(self._async_register_user(name, email, phone, password))
    
    async def _async_register_user(self, name: str, email: str, phone: str, password: str):
        """Handle the async user registration."""
        print(f"[DEBUG] _async_register_user - self.auth_service: {self.auth_service}")
        if not self.auth_service:
            self.show_error("Authentication service not available. Please restart the app.")
            return
            
        try:
            print(f"Attempting to register user: {email}")
            user_metadata = {
                'full_name': name,
                'phone': phone
            }
            print(f"User metadata: {user_metadata}")
            
            # Register the user
            user = await self.auth_service.sign_up(email, password, user_metadata)
            print(f"User registration response: {user}")
            
            if not user:
                raise Exception("No user returned from sign_up")
                
            print(f"Successfully registered user with ID: {user.id}")
            
            # Send email verification
            await self.auth_service.send_verification_email()
            
            # Show success message
            self.on_registration_success(user)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Registration error: {e}\n{error_details}")
            print(f"Registration error: {e}")
            print(f"Error details: {error_details}")
            self.show_error(f"Registration failed: {str(e)}")
        finally:
            self.dismiss_loading()
    
    @mainthread
    def on_registration_success(self, user):
        """Handle successful registration."""
        logger.info(f"User registered: {user.email}")
        self.show_success(
            "Account Created",
            "Your account has been created successfully! "
            "Please check your email to verify your account."
        )
        # Clear the form
        self.clear_form()
        # Switch to login screen after a delay
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.switch_to_login(), 3.0)
    
    def switch_to_login(self):
        """Switch to the restaurant connect screen."""
        self.manager.current = 'restaurant_connect'
    
    def show_loading(self, message="Loading..."):
        """Show a loading dialog."""
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
        """Dismiss the loading dialog if visible."""
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
    
    @mainthread
    def show_success(self, title: str, message: str):
        """Show a success message to the user."""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="Continue",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
