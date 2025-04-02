from datetime import datetime

class OwnedTree:
    def __init__(self, tree_template, purchase_date):
        self.tree = tree_template
        self.purchase_date = purchase_date

    def __repr__(self):
        return f"OwnedTree(name={self.tree.name}, purchase_date={self.purchase_date})"