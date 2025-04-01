from aqt import mw
from aqt.utils import QAction, showInfo
from anki.hooks import addHook
from aqt.gui_hooks import reviewer_did_answer_card
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

# Global variable for coins
coins = 0
coin_label = None  # To hold the coin display widget

# Function to update coins after a review
def on_review_done(card, ease, _review_state):
    global coins

    if ease == 1:  # Again (Fail)
        coins += 1
    elif ease == 2:  # Hard
        coins += 5
    elif ease == 3:  # Good
        coins += 10
    elif ease == 4:  # Easy
        coins += 15
        
    print(f"Coins: {coins}") # TODO: only for debugging
    update_coin_display()

# Use the correct hook
reviewer_did_answer_card.append(on_review_done)

# Function to update coin display in the status bar
def update_coin_display():
    global coin_label
    if coin_label:
        coin_label.setText(f"Coins: {coins}")
    else:
        # In case coin_label doesn't exist yet, create it
        coin_label = QLabel(f"Coins: {coins}")
        mw.statusBar().addWidget(coin_label)

# Function to open the shop
def open_shop():
    # Create the shop window dialog
    shop_window = QDialog(mw)
    shop_window.setWindowTitle("Anki Shop")
    
    # Layout to organize widgets in the shop window
    layout = QVBoxLayout()
    
    # Display coin balance in the shop
    coin_label = QLabel(f"You have {coins} coins.")
    layout.addWidget(coin_label)
    
    # Optionally add a button for closing the shop window
    close_button = QPushButton("Close")
    close_button.clicked.connect(shop_window.close)
    layout.addWidget(close_button)

    # Set the layout and show the window
    shop_window.setLayout(layout)
    shop_window.exec()

# Function to add a shop button to the status bar
def add_shop_button_to_statusbar():
    # Create a button
    shop_button = QPushButton("Open Shop")
    shop_button.clicked.connect(open_shop)
    
    # Add the button to the status bar
    mw.statusBar().addWidget(shop_button)
    print("Shop button added to the status bar.") # TODO: only for debugging

# Run setup
add_shop_button_to_statusbar()
update_coin_display()

print("Anki Forest Plugin loaded and ready.") # TODO: only for debugging