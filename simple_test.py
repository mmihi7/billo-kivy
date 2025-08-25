from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

class TestApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Create a simple layout
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=40,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Add a label
        label = MDLabel(
            text="KivyMD is working!",
            halign="center",
            font_style="H4"
        )
        
        # Add a button
        button = MDRaisedButton(
            text="Click Me",
            pos_hint={'center_x': 0.5}
        )
        button.bind(on_release=self.on_button_click)
        
        layout.add_widget(label)
        layout.add_widget(button)
        
        screen = MDScreen()
        screen.add_widget(layout)
        return screen
    
    def on_button_click(self, instance):
        print("Button clicked!")
        instance.text = "Clicked!"

if __name__ == '__main__':
    TestApp().run()
