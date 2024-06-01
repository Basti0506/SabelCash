import os
import datetime
import threading
import socket
import webbrowser

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.app import App

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField

NAMES = ["Ben", "Bastian", "Miranda", "Melis", "Leart", "Stefan", "Emanuel", "Leopold", "Vincent", "Hayk", "Christian",
         "Lara", "Shayana", "Thea", "Sofia"]

# Prices of items
PRICES = {
    "Five Fruit": 3.50,
    "Virgin Mojito": 3.50,
    "Virgin Sunrise": 3.50,
    "Coconut Kiss": 3.50,
    "Ipanema": 3.50,
    "Eigene Bestellung": 3.50
}

# Colors for the cocktails
COCKTAIL_COLORS = {
    "Five Fruit": "#FF5F5F",  # Red
    "Virgin Mojito": "#79C2FF",  # Blue
    "Virgin Sunrise": "#FFC25A",  # Orange
    "Coconut Kiss": "#8FFF8F",  # Green
    "Ipanema": "#D68FFF",  # Purple
    "Eigene Bestellung": "#FFB76D"  # Light Orange
}

# Variable to store the entered item orders
item_orders = []

class MainScreen(MDScreen):
    name = StringProperty("")
    items = ListProperty([])
    total = NumericProperty(0.00)

    def add_item(self, item):
        self.ids.item_list.add_widget(OneLineListItem(text=item))
        self.items.append(item)
        self.total = sum(PRICES[i] for i in self.items)
        self.update_total_label()
    
    def update_total_label(self):
        self.ids.total_label.text = f"Gesamt: €{self.total:.2f}"
    
    def complete_purchase(self):
        if not self.name:
            Snackbar(text="Name fehlt").show()
            return
        
        def get_amount(dialog, amount):
            try:
                amount_given = float(amount)
                change = amount_given - self.total
                if change < 0:
                    Snackbar(text="Der gezahlte Betrag ist zu wenig").show()
                else:
                    self.show_change_dialog(change)
                    self.save_purchase_history(amount_given, change)
                    self.clear_order()
            except ValueError:
                Snackbar(text="Ungültiger Betrag").show()
        
        dialog = MDDialog(
            title=f"Gesamt: €{self.total:.2f}",
            type="custom",
            content_cls=MDTextField(hint_text="Geben Sie den gezahlten Betrag ein:"),
            buttons=[
                MDFlatButton(text="Abbrechen", on_release=lambda *args: dialog.dismiss()),
                MDRaisedButton(text="OK", on_release=lambda *args: get_amount(dialog, dialog.content_cls.text))
            ]
        )
        dialog.open()
    
    def clear_order(self):
        self.ids.item_list.clear_widgets()
        self.items = []
        self.total = 0.00
        self.update_total_label()
    
    def save_purchase_history(self, amount_given, change):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        purchase = f"{self.name}, {timestamp}, {', '.join(self.items)}, {self.total:.2f}, {change:.2f}\n"
        with open("Verlauf.txt", "a") as file:
            file.write(purchase)
    
    def show_change_dialog(self, change):
        dialog = MDDialog(
            title="Wechselgeld",
            text=f"Wechselgeld: €{change:.2f}",
            buttons=[MDRaisedButton(text="OK", on_release=lambda *args: dialog.dismiss())]
        )
        dialog.open()

class NameEntryDialog(MDDialog):
    def __init__(self, main_screen, **kwargs):
        super().__init__(
            title="Namen eingeben",
            type="custom",
            content_cls=MDTextField(hint_text="Gib deinen Namen ein:"),
            buttons=[
                MDFlatButton(text="Abbrechen", on_release=lambda *args: self.dismiss()),
                MDRaisedButton(text="OK", on_release=lambda *args: self.set_name(main_screen))
            ],
            **kwargs
        )
    
    def set_name(self, main_screen):
        name = self.content_cls.text
        if name not in NAMES:
            MDSnackbar(text="Ungültiger Name").open()
        else:
            main_screen.name = name
            main_screen.ids.name_label.text = name
            self.dismiss()

class CashRegisterApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Dark"
        Builder.load_string(
            
"""
<MainScreen>:

    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 100
            spacing: 20

            Image:
                source: 'Logo_SABEL_Nuernberg_800px (1).png'
                halign: "Left"
                size: self.texture_size
            
        MDLabel:
            id: name_label
            text: ""  # Change this to your desired name
            font_style: "H5"
            halign: "center"
            bold: "true"
            font_size: "36sp"
                
        ScrollView:
            MDList:
                id: item_list

        MDLabel:
            id: total_label
            text: "Gesamt: €0.00"
            font_style: "H5"
            halign: "center"
            bold: True
        
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 20
            
            MDRaisedButton:
                text: "Kauf abschließen"
                on_release: root.complete_purchase()
            
            MDFlatButton:
                text: "Kauf abbrechen"
                md_bg_color: [1, 0.37, 0.37, 1]  # Red
                font_color: "black"
                on_release: root.clear_order()
        
        BoxLayout:
            orientation: 'horizontal'
            spacing: 10
            
            MDCard:
                text_color: [1, 1, 1, 1]  # White
                theme_text_color: "Custom"
                text: "Five Fruit"
                on_release: root.add_item("Five Fruit")
                md_bg_color: [1, 0.37, 0.37, 1]  # Red
                MDLabel:
                    text: "Five Fruit"
                    color: "white"
                    font_size: '36sp'
                    bold: True
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    y: (self.parent.height - self.height) / 2
            
            MDCard:
                text: "Virgin Mojito"
                on_release: root.add_item("Virgin Mojito")
                md_bg_color: [0.48, 0.76, 1, 1]  # Blue
                text_color: [1, 1, 1, 1]  # White
                MDLabel:
                    text: "Virgin Mojito"
                    color: "white"
                    font_size: '36sp'
                    bold: True
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    y: (self.parent.height - self.height) / 2

            
            MDCard:
                on_release: root.add_item("Virgin Sunrise")
                md_bg_color: [1, 0.76, 0.35, 1]  # Orange
                MDLabel:
                    text: "Virgin Sunrise"
                    color: "white"
                    font_size: '36sp'
                    bold: True
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    y: (self.parent.height - self.height) / 2
            
        BoxLayout:
            orientation: 'horizontal'
            spacing: 10
            
            MDCard:
                text: "Coconut Kiss"
                text_color: [1, 1, 1, 1]  # White
                on_release: root.add_item("Coconut Kiss")
                md_bg_color: [0.56, 1, 0.56, 1]  # Green
                MDLabel:
                    text: "Coconut Kiss"
                    color: "white"
                    font_size: '36sp'
                    bold: True
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    y: (self.parent.height - self.height) / 2
                
            
            MDCard:
                text: "Ipanema"
                text_color: [1, 1, 1, 1]  # White
                on_release: root.add_item("Ipanema")
                md_bg_color: [0.84, 0.56, 1, 1]  # Purple
                MDLabel:
                    text: "Ipanema"
                    color: "white"
                    font_size: '36sp'
                    bold: True
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    y: (self.parent.height - self.height) / 2
            
            MDCard:
                text: "Eigene Bestellung"
                text_color: [1, 1, 1, 1]  # White
                on_release: root.add_item("Eigene Bestellung")
                md_bg_color: [1, 0.71, 0.43, 1]  # Light Orange
                MDLabel:
                    text: "Eigene Bestellung"
                    color: "white"
                    font_size: '36sp'
                    bold: True
                    halign: "center"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    y: (self.parent.height - self.height) / 2
""")
        return MainScreen()

    def switch_shift(self):
        NameEntryDialog(self.root).open()

    def on_start(self):
        self.switch_shift()

if __name__ == '__main__':
    CashRegisterApp().run()
