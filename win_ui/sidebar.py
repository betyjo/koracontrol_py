from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtGui import QIcon


class Sidebar(QListWidget):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(120)

        # Add components
        self.add_item("Pump", "ui/assets/pump_off.png")
        self.add_item("Valve", "ui/assets/valve_closed.png")

        self.setDragEnabled(True)

    def add_item(self, name, icon_path):
        item = QListWidgetItem(name)
        item.setIcon(QIcon(icon_path))
        self.addItem(item)