## Features 🚀
1. User-friendly graphical user interface (GUI) using PyQt5 for the cashregister .
2. Flask web server for handling HTTP requests and serving the web application.
3. Real-time updates of the web application using Flask-SocketIO and WebSockets.
4. SQLite database for storing completed purchase history.
5. Sound effect for button click.
6. Option to toggle fullscreen mode using F11.

## How to Use ❓
On startup, click on "Schicht" and then on "Schichtwechsel". Choose your name from the predefined list (See files) and click "Namen setzen."

The main window will display the items ordered, the total cost, and buttons for different items.

To add an item to the order, click the corresponding item button. The selected item will appear in the list, and the total cost will be updated.

To remove an item from the order, select the item in the list and click "Kauf abbrechen."

To complete a purchase, click "Kauf abschließen." Enter the amount given by the customer in the dialog box, and the change will be calculated and displayed in a separate window.

The purchase history can be viewed by clicking the "Verlauf anzeigen" option in the "Verlauf" menu.

To toggle button click sounds, use the "Tastengeräusche" checkbox.

To switch between fullscreen and windowed mode, press F11.

## Web Application 🌐
The Flask web application provides real-time updates of the ordered items. It is accessible at http://localhost:5001/webapp2.html. The web application displays the items ordered in a visually appealing format. Ordered items along with the status can be found on http://localhost:5001/webapp3.html. A simple webapp of the main program with the full feature-set can be found on http://localhost:5001/webapp.html 

## Database 📁
The app uses an SQLite database to store completed purchase history. By doing this we achieve better performance

## Contributing ➕ and Issues 🆘
Contributions to this project are welcome. If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
