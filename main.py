from aqt import mw
from aqt.utils import QAction, showInfo
from anki.hooks import addHook
from anki import hooks 
from aqt.gui_hooks import reviewer_did_answer_card 

# Global variable for coins
coins = 0

# Function to update coins after a review
def on_review_done(card, ease, _review_state):
    global coins
    coins += 10  # Example: increase coins by 10 per review
    print(f"Coins: {coins}")

# Use the correct hook
reviewer_did_answer_card.append(on_review_done)

# Function to open the shop
def open_shop():
    showInfo(f"Welcome to the shop! You have {coins} coins.")
    print(f"Opening shop... Coins: {coins}")

# Add a button to the Tools menu
def setup_menu():
    action = QAction("Open Shop", mw)
    action.triggered.connect(open_shop)
    mw.form.menuTools.addAction(action)
    print("Shop button added to the Tools menu.")

# Run setup
setup_menu()
print("Anki Forest Plugin loaded and ready.")