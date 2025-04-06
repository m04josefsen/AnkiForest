from datetime import datetime

class OwnedTree:
    def __init__(self, tree_template, purchase_date):
        self.tree = tree_template
        self.purchase_date = purchase_date

    def __repr__(self):
        return f"OwnedTree(name={self.tree.name}, purchase_date={self.purchase_date})"

    def to_dict(self):
        return {
            "tree_name": self.tree.name,
            "purchase_date": self.purchase_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data, all_templates):
        matching_template = next((t for t in all_templates if t.name == data["tree_name"]), None)
        if matching_template:
            purchase_date = datetime.fromisoformat(data["purchase_date"])
            return cls(matching_template, purchase_date)
        return None