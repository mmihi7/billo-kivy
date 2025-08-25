from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

# Import Pygments lexer
from pygments.lexers import PythonLexer, KivyLexer

class KVEditor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 5
        self.spacing = 5
        
        # Create code input with Kivy lexer
        self.code_input = CodeInput(
            lexer=KivyLexer(),
            style_name='monokai',
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            selection_color=(0.2, 0.6, 0.8, 0.4),
            font_size='14sp',
            font_name='RobotoMono-Regular.ttf'
        )
        
        # Create preview area
        self.preview = BoxLayout()
        
        # Add widgets to layout
        self.add_widget(self.code_input)
        self.add_widget(self.preview)
        
        # Bind text changes to update preview
        self.code_input.bind(text=self.update_preview)
        
        # Set up keyboard shortcuts
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 's' and 'ctrl' in modifiers:
            self.save_file()
            return True
        return False
    
    def load_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.code_input.text = f.read()
            self.file_path = file_path
        except Exception as e:
            self.show_error(f'Error loading file: {str(e)}')
    
    def save_file(self):
        if not hasattr(self, 'file_path'):
            return
            
        try:
            with open(self.file_path, 'w') as f:
                f.write(self.code_input.text)
        except Exception as e:
            self.show_error(f'Error saving file: {str(e)}')
    
    def update_preview(self, instance, value):
        self.preview.clear_widgets()
        try:
            widget = Builder.load_string(self.code_input.text)
            self.preview.add_widget(widget)
        except Exception as e:
            error_label = Label(text=f'Error: {str(e)}', color=(1, 0.5, 0.5, 1))
            self.preview.add_widget(error_label)
    
    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class KVEditorApp(App):
    def build(self):
        self.editor = KVEditor()
        return self.editor
    
    def on_start(self):
        if len(self.argv) > 1:
            self.editor.load_file(self.argv[1])

if __name__ == '__main__':
    import sys
    KVEditorApp().run()
