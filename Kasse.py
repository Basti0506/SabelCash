import sys
import datetime
import winsound
import threading
import socket
import os
import webbrowser

from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QAction, QMessageBox, QCheckBox, QVBoxLayout, QSizePolicy, QWidget, QHBoxLayout, QMenuBar, QShortcut
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon, QPainter, QMovie, QKeySequence
from PyQt5 import QtCore, QtWidgets

# Create Flask app and configure it
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create the database tables
def create_tables():
    with app.app_context():
        db.create_all()


# List of predefined names
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
    "Five Fruit": QColor("#FF5F5F"),  # Red
    "Virgin Mojito": QColor("#79C2FF"),  # Blue
    "Virgin Sunrise": QColor("#FFC25A"),  # Orange
    "Coconut Kiss": QColor("#8FFF8F"),  # Green
    "Ipanema": QColor("#D68FFF"),  # Purple
    "Eigene Bestellung": QColor("#FFB76D")  # Light Orange
}

# Variable to store the entered item orders
item_orders = []

@app.route('/')
def captcha():
    return render_template('Captcha.html')

@app.route('/haupt')
def index():
    return render_template('index.html', name=main_window.name)


@app.route('/webapp3')
def webapp3():
    return redirect(url_for('webapp3_html'))


@app.route('/webapp3.html')
def webapp3_html():
    # Create a dictionary to map each item to its corresponding color
    item_color = {item: COCKTAIL_COLORS.get(item, '#FDCB9E') for item in item_orders}
    return render_template('webapp3.html', items=item_orders, item_color=item_color)

@app.route('/order_content')
def order_content():
    # Fetch all item orders from the database
    items = [order.item for order in ItemOrder.query.all()]
    return jsonify({'items': items})

@app.route('/webapp2')
def webapp2():
    return redirect(url_for('webapp2_html'))


@app.route('/webapp2.html')
def webapp2_html():
    return render_template('webapp2.html', name=main_window.name, items=item_orders)


@app.route('/webapp')
def webapp_redirect():
    return redirect(url_for('webapp_html'))


@app.route('/webapp.html')
def webapp_html():
    return render_template('webapp.html', name=main_window.name)


@app.route('/websocket')
def websocket():
    return render_template('websocket.html')


@app.route('/history')
def history():
    file_path = os.path.join(app.root_path, 'Verlauf.txt')
    try:
        with open(file_path, 'r') as file:
            history_text = file.read()
    except FileNotFoundError:
        history_text = 'No purchase history found.'

    return render_template('index.html', history=history_text)


@app.route('/purchase_history')
def purchase_history():
    with open("Verlauf.txt", "r") as file:
        history_lines = file.readlines()

    history_text = ""
    for line in history_lines:
        parts = line.strip().split(", ")
        if len(parts) == 5:
            name, timestamp, item, price, change = parts
            formatted_line = f"Name: {name}<br>Date and Time: {timestamp}<br>Item Purchased: {item}<br>Price: €{price}<br>Change: €{change}<br><br>"
            history_text += formatted_line

    return render_template('index.html', history=history_text)



class NameEntryWindow(QtWidgets.QDialog):
    name_set = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(NameEntryWindow, self).__init__(parent)

        # Set window title
        self.setWindowTitle("Namen eingeben")

        # Create label and line edit for name
        self.name_entry_label = QtWidgets.QLabel(self)
        self.name_entry_label.setText("Gib deinen Namen ein:")
        self.name_entry_label.setFont(QFont("Open Sans", 20))
        self.name_entry_label.setStyleSheet("color: black;")

        self.name_entry = QtWidgets.QLineEdit(self)
        self.name_entry.setFont(QFont("Open Sans", 20))

        # Create button to set name
        self.set_name_button = QtWidgets.QPushButton(self)
        self.set_name_button.setText("Namen setzen")
        self.set_name_button.setFont(QFont("Open Sans", 20))
        self.set_name_button.clicked.connect(self.set_name)

        # Create layout for name entry widgets
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.name_entry_label)
        layout.addWidget(self.name_entry)
        layout.addWidget(self.set_name_button)

    def set_name(self):
        # Get entered name
        entered_name = self.name_entry.text()

        # Check if name is valid
        if entered_name not in NAMES:
            QtWidgets.QMessageBox.critical(self, "Fehler", "Ungültiger Name")
            return

        # Emit a signal to notify the parent
        self.name_set.emit(entered_name)
        self.close()

class BootupAnimation(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(BootupAnimation, self).__init__(parent)
        self.bootup_movie = QMovie("Logo_SABEL_Nuernberg_800px (1).png")
        self.setMovie(self.bootup_movie)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.bootup_movie.frameChanged.connect(self.frame_changed)

    def start(self):
        self.bootup_movie.start()

    def frame_changed(self, frame_number):
        if frame_number == self.bootup_movie.frameCount() - 1:
            # The bootup animation has finished, show the main window
            self.parent().show_main_window()

class ChangeWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ChangeWindow, self).__init__(parent)

        # Set window title
        self.setWindowTitle("Wechselgeld")

        # Create label for change
        self.change_label = QtWidgets.QLabel(self)
        self.change_label.setFont(QFont("Open Sans", 30))

        # Create button to close window
        self.ok_button = QtWidgets.QPushButton(self)
        self.ok_button.setText("OK")
        self.ok_button.setFont(QFont("Open Sans", 20))
        self.ok_button.clicked.connect(self.handle_change_accepted)

        # Create layout for change window
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.change_label)
        layout.addWidget(self.ok_button)

    def set_change(self, change):
        self.change_label.setText(f"Wechselgeld: €{change:.2f}")

    def handle_change_accepted(self):
        self.close()


class CashRegister(QtWidgets.QMainWindow):
    def __init__(self):
        super(CashRegister, self).__init__()

        # Set window title
        self.setWindowTitle("Kasse")

        # Create main widget
        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)

        # Set background color of the main widget
        main_widget.setStyleSheet("background-color: #FFF9F1;")

        # Create layout for the main widget
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create top layout for the name and logo
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(20)
        main_layout.addLayout(top_layout)

        # Create logo label
        logo_label = QtWidgets.QLabel(main_widget)
        logo_pixmap = QPixmap("Logo_SABEL_Nuernberg_800px (1).png")
        logo_pixmap = logo_pixmap.scaledToHeight(100)
        logo_label.setPixmap(logo_pixmap)
        top_layout.addWidget(logo_label)

        # Create menubar
        menubar = QMenuBar(main_widget)
        menubar.setStyleSheet("background-color: #FFF9F1; color: black;")
        menubar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_layout.addWidget(menubar)

        # Create actions for options menu
        sound_action = QAction("Tastengeräusche", self)
        sound_action.setCheckable(True)
        sound_action.setChecked(True)
        sound_action.triggered.connect(self.toggle_sound)

        # Create actions for history menu
        show_history_action = QAction("Verlauf anzeigen", self)
        show_history_action.triggered.connect(self.show_purchase_history)

        # Create actions for shift menu
        switch_shift_action = QAction("Schichtwechsel", self)
        switch_shift_action.triggered.connect(self.switch_shift)

        # Create actions for server menu
        server_status_action = QAction("Serverstatus", self)
        server_status_action.triggered.connect(self.show_server_status)

        # Create actions for about menu
        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about_dialog)

        # Create action for website menu
        website_action = QAction("Öffne Webseite", self)
        website_action.triggered.connect(self.open_website)

        # Add actions to menus
        options_menu = menubar.addMenu("Optionen")
        options_menu.addAction(sound_action)
        history_menu = menubar.addMenu("Verlauf")
        history_menu.addAction(show_history_action)
        shift_menu = menubar.addMenu("Schicht")
        shift_menu.addAction(switch_shift_action)
        server_menu = menubar.addMenu("Server")
        server_menu.addAction(server_status_action)
        about_menu = menubar.addMenu("Über")
        about_menu.addAction(about_action)
        website_menu = menubar.addMenu("Webseite")  # Added "Webseite" menu
        website_menu.addAction(website_action)

        # Create label for name
        self.name_label = QtWidgets.QLabel(main_widget)
        self.name_label.setText("")
        self.name_label.setFont(QFont("Open Sans", 30))
        self.name_label.setStyleSheet("color: black;")
        self.name_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        top_layout.addWidget(self.name_label)

        # Create list widget for items
        self.item_list = QtWidgets.QListWidget(main_widget)
        self.item_list.setFont(QFont("Open Sans", 20))
        main_layout.addWidget(self.item_list)

        # Create label for total cost
        self.total_label = QtWidgets.QLabel(main_widget)
        self.total_label.setText("Gesamt: €0.00")
        self.total_label.setFont(QFont("Open Sans", 25))
        self.total_label.setStyleSheet("color: black;")
        self.total_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        main_layout.addWidget(self.total_label)

        # Create buttons for items
        button_layout = QtWidgets.QGridLayout()
        for row, item in enumerate(PRICES):
            button = QtWidgets.QPushButton(main_widget)
            button.setText(item)
            button.setFont(QFont("Open Sans", 20))
            button.setStyleSheet(
                f"background-color: {COCKTAIL_COLORS[item].name()}; color: black; border: none; border-radius: 30px;"
                f"padding: 10px;"
            )
            button.clicked.connect(lambda checked, item=item: self.add_item(item))
            button_layout.addWidget(button, row // 3, row % 3)

        main_layout.addLayout(button_layout)

        # Create buttons layout for completing and canceling purchase
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        main_layout.addLayout(buttons_layout)

        # Create button for completing purchase
        complete_button = QtWidgets.QPushButton(main_widget)
        complete_button.setText("Kauf abschließen")
        complete_button.setFont(QFont("Open Sans", 20))
        complete_button.setStyleSheet(
            "background-color: #FFD700; color: black; border-radius: 30px; padding: 10px;"
        )
        complete_button.clicked.connect(self.complete_purchase)
        buttons_layout.addWidget(complete_button)

        # Create button for canceling purchase
        cancel_button = QtWidgets.QPushButton(main_widget)
        cancel_button.setText("Kauf abbrechen")
        cancel_button.setFont(QFont("Open Sans", 20))
        cancel_button.setStyleSheet(
            "background-color: #FF0000; color: #FFFFFF; border-radius: 30px; padding: 10px;"
        )
        cancel_button.clicked.connect(self.cancel_purchase)
        buttons_layout.addWidget(cancel_button)

        # Create checkbox for enabling/disabling button click sound
        self.sound_checkbox = QCheckBox("Tastengeräusch", main_widget)
        self.sound_checkbox.setFont(QFont("Open Sans", 14))
        self.sound_checkbox.setChecked(True)
        main_layout.addWidget(self.sound_checkbox)

        # Initialize the purchase history
        self.history = []
        self.name = ""  # Added variable to store the entered name

        # Start the listener thread
        self.start_listener_thread()

        # Make the window fullscreenable with F11 or CTRL+Enter
        shortcut = QShortcut(QKeySequence("F11"), self)
        shortcut.activated.connect(self.toggle_fullscreen)

        # Set the program icon
        self.setWindowIcon(QIcon("program_icon.png"))

        # Create a loading animation
        self.loading_label = QtWidgets.QLabel(main_widget)
        loading_movie = QMovie("loading.gif")
        self.loading_label.setMovie(loading_movie)
        loading_movie.start()
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.loading_label)

    def start_listener_thread(self):
        listener_thread = threading.Thread(target=self.item_listener)
        listener_thread.daemon = True
        listener_thread.start()

    def item_listener(self):
        while True:
            if len(item_orders) > 0:
                item = item_orders.pop(0)
                print(f"Received item order: {item}")
                # Emit a signal to update the web app with the new item orders
                socketio.emit('update_order_content', {'items': item_orders}, namespace='/websocket')
            QtCore.QThread.sleep(1)

    def add_item(self, item):
        self.item_list.addItem(item)
        total_cost = sum(PRICES[self.item_list.item(i).text()] for i in range(self.item_list.count()))
        self.total_label.setText(f"Gesamt: €{total_cost:.2f}")
        self.button_click_sound()

        # Add the item to the item_orders list
        item_orders.append(item)

        # Emit a signal to update the web app with the new item orders
        socketio.emit('update_order_content', {'items': item_orders}, namespace='/websocket')

    def delete_selected_item(self):
        selected_item = self.item_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            self.item_list.takeItem(self.item_list.row(selected_item))
            total_cost = sum(PRICES[self.item_list.item(i).text()] for i in range(self.item_list.count()))
            self.total_label.setText(f"Gesamt: €{total_cost:.2f}")
            self.button_click_sound()

            # Remove the item from the item_orders list
            item_orders.remove(item_text)

            # Emit a signal to update the web app with the new item orders
            socketio.emit('update_order_content', {'items': item_orders}, namespace='/websocket')

    def complete_purchase(self):
        name = self.name_label.text()
        if not name:
            QtWidgets.QMessageBox.critical(self, "Fehler", "Name fehlt")
            return

        items = [self.item_list.item(i).text() for i in range(self.item_list.count())]
        total_cost = sum(PRICES[item] for item in items)

        amount_given, ok = QtWidgets.QInputDialog.getDouble(
            self, "Zahlung", f"Gesamt: €{total_cost:.2f}\nGeben Sie den gezahlten Betrag ein:"
        )
        if not ok:
            return

        change = amount_given - total_cost
        if change < 0:
            QtWidgets.QMessageBox.critical(self, "Fehler", "Der gezahlte Betrag ist zu wenig")
            return

        self.show_change_window(change)
        self.save_purchase_history(name, items, total_cost, amount_given, change)
        self.clear_order()

    def cancel_purchase(self):
        self.clear_order()

    def switch_shift(self):
        name_entry_window = NameEntryWindow(self)
        name_entry_window.name_set.connect(self.update_name)
        name_entry_window.exec_()

    def update_name(self, name):
        self.name = name  # Set the entered name
        self.name_label.setText(name)

    def show_purchase_history(self):
        with open("Verlauf.txt", "r") as file:
            history_text = file.read()
        self.show_message_box("Sabelsommerfest 2023 G9a", history_text)

    def show_server_status(self):
        server_status = "Server: Not Running"
        if app.config.get('SERVER_RUNNING', False):
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            server_status = f"Server: Running\nIP: {ip}:5001"
        self.show_message_box("Server Status", server_status)

    def show_about_dialog(self):
        self.show_message_box("Über", "Version: 0.8c Fast_fertig")

    def open_website(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = 5001
        url = f"http://{ip}:{port}"
        webbrowser.open(url)

    def show_change_window(self, change):
        change_window = ChangeWindow(self)
        change_window.set_change(change)
        change_window.exec_()

    def clear_order(self):
        self.item_list.clear()
        self.total_label.setText("Gesamt: €0.00")

    def save_purchase_history(self, name, items, total_cost, amount_given, change):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        purchase = f"{name}, {timestamp}, {', '.join(items)}, {total_cost:.2f}, {change:.2f}\n"
        with open("Verlauf.txt", "a") as file:
            file.write(purchase)

    def show_message_box(self, title, message):
        message_box = QtWidgets.QMessageBox()
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.exec_()

    def button_click_sound(self):
        if self.sound_checkbox.isChecked():
            winsound.Beep(1000, 100)

    def toggle_sound(self, checked):
        if checked:
            winsound.PlaySound("SystemDefault", winsound.SND_ALIAS)
        else:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, event):
        event.accept()


def start_flask():
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)


if __name__ == '__main__':
    # Create the database tables
    create_tables()


    # Define the database model for item orders
    class ItemOrder(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        item = db.Column(db.String(100), nullable=False)

        def __repr__(self):
            return f"<ItemOrder {self.item}>"


    socketio = SocketIO(app)

    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # Create the application instance
    app = QApplication(sys.argv)
    app.setApplicationName("Kasse")
    app.setQuitOnLastWindowClosed(False)

    # Set stylesheet for a modern look
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f2f2f2"))  # Light Gray
    palette.setColor(QPalette.WindowText, QColor("#333333"))  # Dark Gray
    palette.setColor(QPalette.Base, QColor("#ffffff"))  # White
    palette.setColor(QPalette.Button, QColor("#555555"))  # Dark Gray
    palette.setColor(QPalette.ButtonText, QColor("#ffffff"))  # White
    palette.setColor(QPalette.Highlight, QColor("#666666"))  # Dark Gray
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))  # White
    app.setPalette(palette)

    # Create the main window
    main_window = CashRegister()
    main_window.show()

    # Start the event loop
    sys.exit(app.exec_())