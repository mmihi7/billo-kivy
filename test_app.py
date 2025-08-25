from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBody, MDList
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.toolbar import Toolbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from test_data import get_test_data

# Main KV string
KV = '''
<OrderItem@OneLineAvatarIconListItem>:
    text: ''
    quantity: 1
    unit_price: 0
    server_initials: ''
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        padding: [dp(10), 0, 0, 0]
        
        BoxLayout:
            MDLabel:
                text: root.text
                theme_text_color: 'Primary'
                size_hint_x: 0.7
                
            MDLabel:
                text: f"{root.quantity} x KES {root.unit_price:,.0f}"
                theme_text_color: 'Secondary'
                size_hint_x: 0.3
                halign: 'right'
                
        MDLabel:
            text: f"Served by: {root.server_initials}"
            theme_text_color: 'Secondary'
            font_style: 'Caption'
            size_hint_y: None
            height: dp(16)

<PayButton@MDRaisedButton>:
    size_hint: None, None
    size: dp(120), dp(48)
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    md_bg_color: 0.2, 0.6, 0.3, 1
    text_color: 1, 1, 1, 1

<CustomerTab@MDCard>:
    tab_number: ''
    customer_name: ''
    total: 0
    orders: []
    
    orientation: 'vertical'
    size_hint: 0.9, None
    height: dp(500)
    pos_hint: {'center_x': 0.5, 'top': 0.9}
    padding: dp(16)
    spacing: dp(10)
    elevation: 4
    
    MDLabel:
        text: f"Tab #{root.tab_number}"
        font_style: 'H6'
        size_hint_y: None
        height: dp(40)
        
    MDLabel:
        text: f"Customer: {root.customer_name}"
        font_style: 'Subtitle1'
        size_hint_y: None
        height: dp(30)
    
    ScrollView:
        size_hint: 1, 1
        
        MDList:
            id: orders_list
            spacing: dp(8)
    
    BoxLayout:
        size_hint_y: None
        height: dp(60)
        spacing: dp(10)
        
        MDLabel:
            text: f"Total: KES {root.total:,.2f}"
            font_style: 'H6'
            halign: 'left'
            valign: 'center'
            
        PayButton:
            text: 'PAY NOW'
            on_release: root.process_payment()

ScreenManager:
    id: screen_manager
    
    Screen:
        name: 'tabs_list'
        
        MDBoxLayout:
            orientation: 'vertical'
            
            Toolbar:
                id: toolbar
                title: 'Loading...'
                elevation: 10
                md_bg_color: app.theme_cls.primary_color
                specific_text_color: 1, 1, 1, 1
                right_action_items: [['refresh', lambda x: app.refresh_tabs()]]
                
            ScrollView:
                MDList:
                    id: tabs_list
                    padding: dp(10)
                    spacing: dp(10)
                    
                    MDFillRoundFlatButton:
                        text: 'Refresh Tabs'
                        size_hint: 1, None
                        height: dp(48)
                        on_release: app.refresh_tabs()
                        pos_hint: {'center_x': 0.5}
    
    Screen:
        name: 'tab_detail'
        
        CustomerTab:
            id: customer_tab
            
        MDFloatingActionButton:
            icon: 'arrow-left'
            elevation: 8
            pos_hint: {'x': 0.02, 'top': 0.98}
            on_release: app.root.current = 'tabs_list'
'''

class OrderItem(OneLineAvatarIconListItem):
    text = StringProperty()
    quantity = NumericProperty(1)
    unit_price = NumericProperty(0)
    server_initials = StringProperty('')
    
    def on_checkbox_active(self, active):
        # Handle checkbox state change if needed
        pass

class CustomerTab(MDCard):
    tab_number = StringProperty('')
    customer_name = StringProperty('')
    total = NumericProperty(0)
    orders = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(orders=self.update_orders_list)
    
    def update_orders_list(self, instance, orders):
        self.ids.orders_list.clear_widgets()
        for order in orders:
            item = OrderItem(
                text=order['name'],
                quantity=order['quantity'],
                unit_price=order['unit_price'],
                server_initials=order['server_initials']
            )
            self.ids.orders_list.add_widget(item)
    
    def process_payment(self):
        app = App.get_running_app()
        app.show_payment_screen(self.tab_number, self.total)

class TestApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = get_test_data()
        
    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        return Builder.load_string(KV)
    
    def on_start(self):
        # Set the restaurant name in the toolbar
        self.root.get_screen('tabs_list').ids.toolbar.title = self.data['restaurant']['name']
        self.refresh_tabs()
    
    def refresh_tabs(self):
        # Clear existing tabs
        tabs_list = self.root.get_screen('tabs_list').ids.tabs_list
        tabs_list.clear_widgets()
        
        # Add refresh button at the top
        refresh_btn = MDRaisedButton(
            text='Refresh Tabs',
            size_hint=(1, None),
            height=dp(48),
            on_release=lambda x: self.refresh_tabs()
        )
        tabs_list.add_widget(refresh_btn)
        
        # Add customer tabs
        for tab in self.data['tabs']:
            btn = MDRaisedButton(
                text=f"Tab #{tab['number']}: {tab['customer_name']} - KES {tab['total']:,.2f}",
                size_hint=(1, None),
                height=dp(60),
                on_release=lambda x, t=tab: self.show_tab_detail(t)
            )
            tabs_list.add_widget(btn)
    
    def show_tab_detail(self, tab_data):
        tab_screen = self.root.get_screen('tab_detail')
        customer_tab = tab_screen.ids.customer_tab
        
        customer_tab.tab_number = str(tab_data['number'])
        customer_tab.customer_name = tab_data['customer_name']
        customer_tab.total = tab_data['total']
        customer_tab.orders = tab_data['orders']
        
        self.root.current = 'tab_detail'
    
    def show_payment_screen(self, tab_number, amount):
        from kivymd.uix.dialog import MDDialog
        
        dialog = MDDialog(
            title=f"Process Payment - Tab #{tab_number}",
            text=f"Process payment of KES {amount:,.2f}?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CONFIRM PAYMENT",
                    on_release=lambda x: self.process_payment(tab_number, amount, dialog)
                ),
            ],
        )
        dialog.open()
    
    def process_payment(self, tab_number, amount, dialog):
        # In a real app, this would process the payment
        print(f"Processing payment for Tab #{tab_number}: KES {amount:,.2f}")
        dialog.dismiss()
        
        # Show success message
        from kivymd.toast import toast
        toast(f"Payment of KES {amount:,.2f} processed successfully!")
        
        # Return to tabs list
        self.root.current = 'tabs_list'
        self.refresh_tabs()

if __name__ == '__main__':
    TestApp().run()