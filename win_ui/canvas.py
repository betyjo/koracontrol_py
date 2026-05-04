from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from components import DraggableComponent


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")

        self.setAcceptDrops(True)
        self.tag_values = {}
        self.components = []   # 🔥 IMPORTANT

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):

        self.tag_values[comp.id] = False
        item = event.source().currentItem().text()

        if item == "Pump":
            comp = DraggableComponent(
                "pump",
                "ui/assets/pump_off.png",
                "ui/assets/pump_on.png",
                self
            )

        elif item == "Valve":
            comp = DraggableComponent(
                "valve",
                "ui/assets/valve_closed.png",
                "ui/assets/valve_open.png",
                self
            )
        else:
            return

        comp.move(event.position().toPoint())
        comp.show()

        self.components.append(comp)   # 🔥 TRACK IT

        print("Added:", comp.get_data())
def get_all_components(self):
 return [c.get_data() for c in self.components]

def update_tag(self, comp):
    if comp.tag:
        self.tag_values[comp.tag] = comp.state
        print("Updated:", self.tag_values)