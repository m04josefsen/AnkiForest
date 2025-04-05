from aqt import mw
from aqt.utils import QAction, showInfo
from anki.hooks import addHook
from aqt.gui_hooks import reviewer_did_answer_card
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QGridLayout, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QPainter, QTransform
from PyQt6.QtCore import Qt


import random
import datetime

# TODO: Example trees, would need to change to be able to track, maybe everyone needs their own class
from .tree_template import TreeTemplate
from .owned_tree import OwnedTree
import os

BASE_DIR = os.path.dirname(__file__)  # Finds main.py

trees = [
    TreeTemplate("Oak", 0, os.path.join(BASE_DIR, "assets/img/oak.webp")),
    TreeTemplate("Pine", 150, os.path.join(BASE_DIR, "assets/img/pine.webp")),
    TreeTemplate("Cherry Blossom", 200, os.path.join(BASE_DIR, "assets/img/cherry.webp")),
]

owned_trees = [
    OwnedTree(trees[0], datetime.datetime.now()), 
    OwnedTree(trees[1], datetime.datetime.now()), 
    OwnedTree(trees[2], datetime.datetime.now() - datetime.timedelta(weeks=2)),  
    OwnedTree(trees[0], datetime.datetime.now() - datetime.timedelta(weeks=4)), 
    OwnedTree(trees[1], datetime.datetime.now() - datetime.timedelta(days=50)), 
    OwnedTree(trees[2], datetime.datetime.now() - datetime.timedelta(days=100)), 
    OwnedTree(trees[0], datetime.datetime.now() - datetime.timedelta(days=200)), 
    OwnedTree(trees[1], datetime.datetime.now() - datetime.timedelta(days=365)), 
    OwnedTree(trees[2], datetime.datetime.now() - datetime.timedelta(days=400)),
    OwnedTree(trees[0], datetime.datetime.now() - datetime.timedelta(days=500)), 
]

# Global variable for coins
coins = 0
coin_label = None  # To hold the coin display widget
page_index = 0
forest_window = None
window_height = 600
window_width = 600


"""
0 = this week
1 = this month
2 = this year
3 = all time
TODO: previous month, years etc...
"""

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
    global window_width
    global window_height

    # Create the shop window dialog
    shop_window = QDialog(mw)
    shop_window.setWindowTitle("Shop")
    shop_window.setFixedSize(window_width, window_height)
    
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
    global owned_trees
    if coins >= tree.price:
        coins -= tree.price
        # TODO: denner er dårlig, kanskje bruke dictionary med count, JA, og if 0 så vises den ikke
        owned_tree = OwnedTree(tree, datetime.datetime.now())
        owned_trees.append(owned_tree)
        print(f"Bought {tree.name}! Remaining coins: {coins}")
        update_coin_display()
    else:
        print("Not enough coins!")

# Function to add a shop button to the status bar
def add_shop_button_to_statusbar():
    # Create a button
    shop_button = QPushButton("Open Shop")
    shop_button.clicked.connect(open_shop)
    
    # Add the button to the status bar
    mw.statusBar().addWidget(shop_button)
    print("Shop button added to the status bar.") # TODO: only for debugging

def open_forest():
    global forest_window
    global window_height
    global window_width

    # Create the forest window dialog
    forest_window = QDialog(mw)
    forest_window.setWindowTitle("Forest")
    forest_window.setFixedSize(window_width, window_height)

    # Layout to organize widgets in the forest window
    layout = QVBoxLayout()

    # Pass the layout to the update function
    update_forest_display(layout)  # Populate the layout with trees and navigation

    # Button to close the forest window
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
    
def update_forest_display(layout):
    global page_index

    # Clear the existing layout
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            inner_layout = item.layout()
            for j in reversed(range(inner_layout.count())):
                inner_item = inner_layout.itemAt(j)
                if inner_item.widget():
                    inner_item.widget().deleteLater()
            layout.removeItem(inner_layout)

    if page_index == 0:
        period_label = QLabel("This week")
    elif page_index == 1:
        period_label = QLabel("This month") 
    elif page_index == 2:
        period_label = QLabel("This year")
    else:
        period_label = QLabel("All time")
    layout.addWidget(period_label)

    trees_for_period = get_trees_for_period(page_index)
    random.shuffle(trees_for_period)

    # Set up isometric scene
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setFixedSize(window_width - 20, window_height - 150)
    scene.setSceneRect(0, 0, window_width - 20, window_height - 150)

    # Set up background image (grass field) and apply isometric rotation
    background = QPixmap(os.path.join(BASE_DIR, "assets/img/temptile.jpg"))
    transform = QTransform()
    transform.rotate(45)  # Rotate the background 45 degrees (isometric angle)
    rotated_background = background.transformed(transform)
    rotated_background = rotated_background.scaled(view.width(), view.height())
    background_item = QGraphicsPixmapItem(rotated_background)
    background_item.setZValue(-1)  # Ensure background stays at the back
    scene.addItem(background_item)

    # Define isometric grid
    grid_width = 6   # columns
    grid_height = 4  # rows
    tile_width = 60
    tile_height = 30

    BASE_SCALE = 0.2
    used_positions = set()
    max_attempts = 100

    for tree in trees_for_period:
        pixmap = QPixmap(tree.tree.asset)

        attempts = 0
        while attempts < max_attempts:
            grid_x = random.randint(0, grid_width - 1)
            grid_y = random.randint(0, grid_height - 1)
            if (grid_x, grid_y) in used_positions:
                attempts += 1
                continue

            iso_x = (grid_x - grid_y) * tile_width + view.width() // 2
            iso_y = (grid_x + grid_y) * tile_height // 2 + 60

            # Check if within diamond bounds
            center_x = view.width() // 2
            center_y = view.height() // 2
            dx = abs(iso_x - center_x)
            dy = abs(iso_y - center_y)
            diamond_width = grid_width * tile_width
            diamond_height = grid_height * tile_height

            if (dx / (diamond_width / 2) + dy / (diamond_height / 2)) <= 1:
                used_positions.add((grid_x, grid_y))
                break
            attempts += 1

        # Scale based on depth
        depth_factor = 1.0 - (grid_y * 0.05)
        scale_factor = BASE_SCALE * depth_factor
        scaled_pixmap = pixmap.scaled(
            pixmap.width() * scale_factor,
            pixmap.height() * scale_factor,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        item = QGraphicsPixmapItem(scaled_pixmap)
        item.setOffset(-scaled_pixmap.width() / 2, -scaled_pixmap.height())
        item.setPos(iso_x, iso_y)
        item.setZValue(iso_y)
        scene.addItem(item)

    layout.addWidget(view)

    # Navigation
    nav_layout = QHBoxLayout()
    prev_button = QPushButton("Previous")
    next_button = QPushButton("Next")
    prev_button.clicked.connect(prev_page)
    next_button.clicked.connect(next_page)
    nav_layout.addWidget(prev_button)
    nav_layout.addWidget(next_button)
    layout.addLayout(nav_layout)

# Function to go to next page in the forest window
def next_page():
    global page_index
    if page_index < 3:
        page_index += 1
    # Loops back if on last page
    else:
        page_index = 0
    
    # Fetch the layout of the forest window and pass it to update_forest_display
    layout = forest_window.layout()  # Access layout from the forest window
    update_forest_display(layout)

# Function to go to the previous page in the forest window
def prev_page():
    global page_index
    if page_index > 0:
        page_index -= 1
    # Loops to the back if on first page
    else:
        page_index = 2

    # Fetch the layout of the forest window and pass it to update_forest_display
    layout = forest_window.layout()  # Access layout from the forest window
    update_forest_display(layout)

def get_trees_for_period(page_index):
    now = datetime.datetime.now()
    
    if page_index == 0:  # This week
        start_date = now - datetime.timedelta(days=now.weekday())  # Monday this week
    elif page_index == 1:  # This month
        start_date = now.replace(day=1)  # First of this month
    elif page_index == 2:  # This year
        start_date = now.replace(month=1, day=1)  # First of January
    else:  # All time
        return owned_trees

    return [tree for tree in owned_trees if tree.purchase_date >= start_date]

# Run setup
add_shop_button_to_statusbar()
add_forest_button_to_statusbar()
update_coin_display()

print("Anki Forest Plugin loaded and ready.") # TODO: only for debugging