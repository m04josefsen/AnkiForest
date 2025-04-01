from aqt import mw
from aqt.utils import QAction, showInfo
from anki.hooks import addHook
from aqt.gui_hooks import reviewer_did_answer_card
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap

# TODO: Example trees, would need to change to be able to track, maybe everyone needs their own class
from .tree import Tree
import os

BASE_DIR = os.path.dirname(__file__)  # Finds main.py

trees = [
    Tree("Oak", 100, os.path.join(BASE_DIR, "assets/img/oak.webp")),
    Tree("Pine", 150, os.path.join(BASE_DIR, "assets/img/pine.webp")),
    Tree("Cherry Blossom", 200, os.path.join(BASE_DIR, "assets/img/cherry.webp")),
]

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
    shop_window.setWindowTitle("Shop")
    
    # Layout to organize widgets in the shop window
    layout = QVBoxLayout()

    # Loop through trees and display them
    for tree in trees:
        tree_layout = QHBoxLayout()
        
        # Picture of tree
        image_label = QLabel()
        pixmap = QPixmap(tree.asset)
        pixmap = pixmap.scaled(50, 50)  # 50 x 50 pixels
        image_label.setPixmap(pixmap)
        tree_layout.addWidget(image_label)

        # Name and Price
        info_label = QLabel(f"{tree.name} - {tree.price} coins")
        tree_layout.addWidget(info_label)

        # Buy button
        buy_button = QPushButton("Buy")
        buy_button.clicked.connect(lambda _, t=tree: buy_tree(t))
        tree_layout.addWidget(buy_button)

        # Add trees to main layout
        layout.addLayout(tree_layout)

    # Button to close shop window
    close_button = QPushButton("Close")
    close_button.clicked.connect(shop_window.close)
    layout.addWidget(close_button)

    # Set the layout and show the window
    shop_window.setLayout(layout)
    shop_window.exec()

def buy_tree(tree):
    global coins
    if coins >= tree.price:
        coins -= tree.price
        print(f"Bought {tree.name}! Remaining coins: {coins}")
        update_coin_display()
    else:
        print("Not enough coins!")

"""
def open_shop():
    # Create the shop window dialog
    shop_window = QDialog(mw)
    shop_window.setWindowTitle("Anki Shop")
    
    # Layout to organize widgets in the shop window
    layout = QVBoxLayout()
    
    # Display coin balance in the shop
    coin_label = QLabel(f"You have {coins} coins.")
    layout.addWidget(coin_label)
    
    # Button to close shop window
    close_button = QPushButton("Close")
    close_button.clicked.connect(shop_window.close)
    layout.addWidget(close_button)

    # Set the layout and show the window
    shop_window.setLayout(layout)
    shop_window.exec()
"""

# Function to add a shop button to the status bar
def add_shop_button_to_statusbar():
    # Create a button
    shop_button = QPushButton("Open Shop")
    shop_button.clicked.connect(open_shop)
    
    # Add the button to the status bar
    mw.statusBar().addWidget(shop_button)
    print("Shop button added to the status bar.") # TODO: only for debugging

def open_forest():
    # Create the shop window dialog
    forest_window = QDialog(mw)
    forest_window.setWindowTitle("Forest")
    
    # Layout to organize widgets in the forest window
    layout = QVBoxLayout()
    
    # Display coin balance in the forest window
    coin_label = QLabel(f"You have {coins} coins.")
    layout.addWidget(coin_label)
    
    # Button to close forest window
    close_button = QPushButton("Close")
    close_button.clicked.connect(forest_window.close)
    layout.addWidget(close_button)

    # Set the layout and show the window
    forest_window.setLayout(layout)
    forest_window.exec()

# Function to add a forest button to the status bar
# TODO: kan kanskje bli en metode med shop button, må bare ta inn forest/shop
def add_forest_button_to_statusbar():
    # Create a button
    forest_button = QPushButton("Open Forest")
    forest_button.clicked.connect(open_forest)

    # Add the button to the status bar
    mw.statusBar().addWidget(forest_button)
    print("Forest button added to the status bar.") #TODO: only for debugging

# Run setup
add_shop_button_to_statusbar()
add_forest_button_to_statusbar()
update_coin_display()

print("Anki Forest Plugin loaded and ready.") # TODO: only for debugging