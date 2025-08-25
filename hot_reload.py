from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.utils.hot_reload_viewer import HotReloadViewer

KV = '''
<HotReloadApp>:
    orientation: 'horizontal'
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Edit KV File (Ctrl+S to save)'
            size_hint_y: None
            height: dp(30)
        TextInput:
            id: code_input
            font_name: 'RobotoMono-Regular.ttf'
            font_size: '14sp'
            background_color: 0.1, 0.1, 0.1, 1
            foreground_color: 1, 1, 1, 1
            cursor_color: 1, 1, 1, 1
            selection_color: 0.2, 0.6, 0.8, 0.4
            size_hint_x: 1
            on_text: app.schedule_update()
    HotReloadViewer:
        size_hint_x: 0.4
        path: app.kv_file_path
        errors: True
        errors_text_color: 1, 1, 0, 1
        errors_background_color: 0.1, 0.1, 0.1, 1
'''

class HotReloadApp(MDApp):
    kv_file_path = StringProperty('')
    _update_trigger = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self._update_trigger = Clock.create_trigger(self._update_file, 0.5)
        root = Builder.load_string(KV)
        return root

    def on_start(self):
        # Load initial content if file exists
        try:
            with open(self.kv_file_path, 'r') as f:
                self.root.ids.code_input.text = f.read()
        except FileNotFoundError:
            print(f"File not found: {self.kv_file_path}")

    def schedule_update(self):
        self._update_trigger()

    def _update_file(self, dt):
        try:
            with open(self.kv_file_path, 'w') as f:
                f.write(self.root.ids.code_input.text)
        except Exception as e:
            print(f"Error updating file: {e}")

def start_hot_reload(kv_file_path):
    """Start the hot reload app with the specified KV file."""
    app = HotReloadApp()
    app.kv_file_path = kv_file_path
    app.run()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        start_hot_reload(sys.argv[1])
    else:
        print("Usage: python hot_reload.py path/to/your/file.kv")
