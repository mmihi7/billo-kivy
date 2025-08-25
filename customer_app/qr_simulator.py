from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
import random
import string

class QRSimulator:
    """
    A QR code simulator for testing on non-Android platforms.
    This simulates the behavior of a QR code scanner by generating test QR data.
    """
    
    def __init__(self, callback):
        """
        Initialize the QR simulator.
        
        Args:
            callback: Function to call when QR code is "scanned".
                     Will be called with the scanned data as argument.
        """
        self.callback = callback
        self.popup = None
    
    def show_simulator(self):
        """Show the QR code simulator popup."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add a label with instructions
        content.add_widget(Label(
            text="QR Code Simulator\n\n"
                 "This is a test interface that simulates QR code scanning.\n"
                 "Click 'Simulate Scan' to generate a test QR code.",
            halign='center',
            valign='middle',
            size_hint_y=0.6
        ))
        
        # Add buttons
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        
        # Button to simulate a successful scan
        scan_btn = Button(
            text='Simulate Scan',
            size_hint=(0.8, 1),
            pos_hint={'center_x': 0.5}
        )
        scan_btn.bind(on_release=self._on_scan_clicked)
        
        # Button to close the simulator
        close_btn = Button(
            text='Close',
            size_hint=(0.8, 1),
            pos_hint={'center_x': 0.5}
        )
        close_btn.bind(on_release=self._dismiss_popup)
        
        btn_layout.add_widget(scan_btn)
        content.add_widget(btn_layout)
        content.add_widget(close_btn)
        
        # Create and open the popup
        self.popup = Popup(
            title='QR Code Simulator',
            content=content,
            size_hint=(0.8, 0.8)
        )
        self.popup.open()
    
    def _on_scan_clicked(self, instance):
        """Handle the scan button click by generating test data and closing."""
        # Generate some test data that looks like a QR code payload
        test_data = self._generate_test_qr_data()
        
        # Dismiss the popup
        self._dismiss_popup()
        
        # Simulate a small delay as if scanning was happening
        Clock.schedule_once(lambda dt: self._simulate_scan_complete(test_data), 0.5)
    
    def _dismiss_popup(self, *args):
        """Dismiss the popup if it's open."""
        if self.popup:
            self.popup.dismiss()
            self.popup = None
    
    def _simulate_scan_complete(self, data):
        """Simulate the completion of a QR code scan."""
        if self.callback:
            self.callback(data)
    
    @staticmethod
    def _generate_test_qr_data():
        """Generate test data that simulates a QR code payload."""
        # This is just an example - modify as needed for your app
        test_types = [
            lambda: f"user:{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}",
            lambda: f"product:{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}",
            lambda: f"order:{''.join(random.choices(string.digits, k=10))}",
            lambda: f"https://billo.app/pay?amount={random.randint(1, 1000)}&currency=KES"
        ]
        
        # Randomly select a test data type
        return random.choice(test_types)()
