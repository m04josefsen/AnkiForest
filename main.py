from aqt import mw
from aqt.utils import QAction, showInfo
from anki.hooks import addHook 
from aqt.gui_hooks import reviewer_did_answer_card
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QWidget, QGridLayout,
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QScrollArea
)
from PyQt6.QtGui import QPixmap, QPainter, QTransform
from PyQt6.QtCore import Qt

import random
import datetime
import json
import os

# ============================
# Constants and Globals
# ============================

BASE_DIR = os.path.dirname(__file__)  # Finds main.py
SAVE_FILE = os.path.join(BASE_DIR, "user_data.json")

from .tree_template import TreeTemplate
from .owned_tree import OwnedTree

# Example tree templates with color
trees = [
    TreeTemplate("Tree1", 0, os.path.join(BASE_DIR, "assets/img/tree1_green.png"), "Green"),
    TreeTemplate("Tree1", 0, os.path.join(BASE_DIR, "assets/img/tree1_sandy.png"), "Sandy"),
    TreeTemplate("Tree1", 0, os.path.join(BASE_DIR, "assets/img/tree1_teal.png"), "Teal"),
    TreeTemplate("Tree1", 0, os.path.join(BASE_DIR, "assets/img/tree1_yellow.png"), "Yellow"),

    TreeTemplate("Tree2", 0, os.path.join(BASE_DIR, "assets/img/tree2_green.png"), "Green"),
    TreeTemplate("Tree2", 0, os.path.join(BASE_DIR, "assets/img/tree2_sandy.png"), "Sandy"),
    TreeTemplate("Tree2", 0, os.path.join(BASE_DIR, "assets/img/tree2_teal.png"), "Teal"),
    TreeTemplate("Tree2", 0, os.path.join(BASE_DIR, "assets/img/tree2_yellow.png"), "Yellow"),

    TreeTemplate("Tree3", 0, os.path.join(BASE_DIR, "assets/img/tree3_green.png"), "Green"),
    TreeTemplate("Tree3", 0, os.path.join(BASE_DIR, "assets/img/tree3_sandy.png"), "Sandy"),
    TreeTemplate("Tree3", 0, os.path.join(BASE_DIR, "assets/img/tree3_teal.png"), "Teal"),
    TreeTemplate("Tree3", 0, os.path.join(BASE_DIR, "assets/img/tree3_yellow.png"), "Yellow"),

    TreeTemplate("Tree4", 0, os.path.join(BASE_DIR, "assets/img/tree4_green.png"), "Green"),
    TreeTemplate("Tree4", 0, os.path.join(BASE_DIR, "assets/img/tree4_sandy.png"), "Sandy"),
    TreeTemplate("Tree4", 0, os.path.join(BASE_DIR, "assets/img/tree4_teal.png"), "Teal"),
    TreeTemplate("Tree4", 0, os.path.join(BASE_DIR, "assets/img/tree4_yellow.png"), "Yellow"),
]

owned_trees = []  # Will be loaded from file
coins = 0
coin_label = None  # To hold the coin display widget
page_index = 0
forest_window = None
window_height = 600
window_width = 600

# ============================
# Save & Load User Data
# ============================

def save_data():
    data = {
        "coins": coins,
        "owned_trees": [
            {
                "name": tree.tree.name,
                "purchase_date": tree.purchase_date.isoformat(),
            }
            for tree in owned_trees
        ],
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def load_data():
    global coins, owned_trees
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            coins = data.get("coins", 0)
            owned_trees = []
            for t in data.get("owned_trees", []):
                tree_template = next((tr for tr in trees if tr.name == t["name"]), trees[0])
                date = datetime.datetime.fromisoformat(t["purchase_date"])
                owned_trees.append(OwnedTree(tree_template, date))
    except FileNotFoundError:
        coins = 0
        owned_trees = []

# ============================
# Review Hook: Reward Coins
# ============================

def on_review_done(card, ease, _review_state):
    global coins

    if ease == 1: # Again
        coins += 1
    elif ease == 2: # Hard
        coins += 5
    elif ease == 3: # Good
        coins += 10
    elif ease == 4: # Easy
        coins += 15

    print(f"Coins: {coins}")  # Debug only
    update_coin_display()
    save_data()

reviewer_did_answer_card.append(on_review_done)

# ============================
# Status Bar Coin Display
# ============================

def update_coin_display():
    global coin_label
    if coin_label:
        coin_label.setText(f"Coins: {coins}")
    else:
        coin_label = QLabel(f"Coins: {coins}")
        mw.statusBar().addWidget(coin_label)

# ============================
# Shop Functionality
# ============================

def open_shop():
    global window_width, window_height
    shop_window = QDialog(mw)
    shop_window.setWindowTitle("Shop")
    shop_window.setFixedSize(window_width, window_height)

    # Layout for the shop window
    layout = QVBoxLayout()

    # Create a scroll area for the list of trees
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # Create a widget inside the scroll area to hold the tree items
    scroll_widget = QWidget()
    scroll_layout = QVBoxLayout()

    # Group trees by type
    tree_groups = {}
    for tree in trees:
        if tree.name not in tree_groups:
            tree_groups[tree.name] = []
        tree_groups[tree.name].append(tree)

    # Use a grid layout to place trees in rows (with 4 items per row)
    grid_layout = QGridLayout()

    # Track the row and column to place trees
    row, col = 0, 0
    max_columns = 4  # 4 items per row

    # Set the width of each column to ensure all trees fit within the window width
    col_width = window_width // max_columns
    row_height = 150  # Height of each row

    for tree_type, grouped_trees in tree_groups.items():
        # For each tree, create a row with the tree's information and image
        for tree in grouped_trees:
            # Create individual layout for each tree
            row_layout = QVBoxLayout()

            # Display tree image with scaled size to avoid large images
            image_label = QLabel()
            pixmap = QPixmap(tree.asset).scaled(80, 80)  # Fixed size for each tree image
            image_label.setPixmap(pixmap)
            row_layout.addWidget(image_label)

            # Label for tree name and color
            info_label = QLabel(f"{tree_type} ({tree.color}) - {tree.price} coins")
            row_layout.addWidget(info_label)

            # Button to buy tree
            buy_button = QPushButton("Buy")
            buy_button.clicked.connect(lambda _, t=tree: buy_tree(t))
            row_layout.addWidget(buy_button)

            # Add the tree layout to the grid layout
            grid_layout.addLayout(row_layout, row, col)

            # Move to the next column
            col += 1
            if col >= max_columns:
                col = 0
                row += 1

    scroll_widget.setLayout(grid_layout)
    scroll_area.setWidget(scroll_widget)

    layout.addWidget(scroll_area)

    close_button = QPushButton("Close")
    close_button.clicked.connect(shop_window.close)
    layout.addWidget(close_button)

    shop_window.setLayout(layout)
    shop_window.exec()

def buy_tree(tree):
    global coins, owned_trees
    if coins >= tree.price:
        coins -= tree.price
        owned_trees.append(OwnedTree(tree, datetime.datetime.now()))
        print(f"Bought {tree.name}! Remaining coins: {coins}")
        update_coin_display()
        save_data()
    else:
        print("Not enough coins!")


def add_shop_button_to_statusbar():
    shop_button = QPushButton("Open Shop")
    shop_button.clicked.connect(open_shop)
    mw.statusBar().addWidget(shop_button)
    print("Shop button added to the status bar.")

# ============================
# Forest Functionality
# ============================

def open_forest():
    global forest_window
    forest_window = QDialog(mw)
    forest_window.setWindowTitle("Forest")
    forest_window.setFixedSize(window_width, window_height)
    layout = QVBoxLayout()
    update_forest_display(layout)
    close_button = QPushButton("Close")
    close_button.clicked.connect(forest_window.close)
    layout.addWidget(close_button)
    forest_window.setLayout(layout)
    forest_window.exec()


def add_forest_button_to_statusbar():
    forest_button = QPushButton("Open Forest")
    forest_button.clicked.connect(open_forest)
    mw.statusBar().addWidget(forest_button)
    print("Forest button added to the status bar.")


def update_forest_display(layout):
    global page_index

    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            for j in reversed(range(item.layout().count())):
                sub_item = item.layout().itemAt(j)
                if sub_item.widget():
                    sub_item.widget().deleteLater()
            layout.removeItem(item.layout())

    labels = ["This week", "This month", "This year", "All time"]
    layout.addWidget(QLabel(labels[page_index]))

    trees_for_period = get_trees_for_period(page_index)
    random.shuffle(trees_for_period)

    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setFixedSize(window_width - 20, window_height - 150)
    scene.setSceneRect(0, 0, window_width - 20, window_height - 150)

    background = QPixmap(os.path.join(BASE_DIR, "assets/img/tempgrass.png"))
    transform = QTransform()
    transform.rotate(45)
    rotated_background = background.transformed(transform).scaled(view.width(), view.height())
    background_item = QGraphicsPixmapItem(rotated_background)
    background_item.setZValue(-1)
    scene.addItem(background_item)

    grid_width, grid_height = 6, 4
    tile_width, tile_height = 60, 30
    BASE_SCALE = 0.5
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

        depth_factor = 1.0 - (grid_y * 0.05)
        scale_factor = BASE_SCALE * depth_factor
        scaled_pixmap = pixmap.scaled(
            pixmap.width() * scale_factor,
            pixmap.height() * scale_factor,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        item = QGraphicsPixmapItem(scaled_pixmap)
        item.setOffset(-scaled_pixmap.width() / 2, -scaled_pixmap.height())
        item.setPos(iso_x, iso_y)
        item.setZValue(iso_y)
        scene.addItem(item)

    layout.addWidget(view)

    nav_layout = QHBoxLayout()
    prev_button = QPushButton("Previous")
    next_button = QPushButton("Next")
    prev_button.clicked.connect(prev_page)
    next_button.clicked.connect(next_page)
    nav_layout.addWidget(prev_button)
    nav_layout.addWidget(next_button)
    layout.addLayout(nav_layout)


def next_page():
    global page_index
    page_index = (page_index + 1) % 4
    update_forest_display(forest_window.layout())


def prev_page():
    global page_index
    page_index = (page_index - 1) % 4
    update_forest_display(forest_window.layout())


def get_trees_for_period(index):
    now = datetime.datetime.now()
    if index == 0:
        start = now - datetime.timedelta(days=now.weekday())
    elif index == 1:
        start = now.replace(day=1)
    elif index == 2:
        start = now.replace(month=1, day=1)
    else:
        return owned_trees
    return [t for t in owned_trees if t.purchase_date >= start]

# ============================
# Run Setup
# ============================

load_data()
addHook("profileWillClose", save_data)
add_shop_button_to_statusbar()
add_forest_button_to_statusbar()
update_coin_display()
print("Anki Forest Plugin loaded and ready.")
