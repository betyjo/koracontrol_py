import requests
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from components import DraggableComponent
from PyQt6.QtWidgets import QTextEdit
import requests
from PyQt6.QtCore import QTimer

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")

        self.setAcceptDrops(True)

        self.tag_values = {}
        self.components = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.sync_from_backend)
        self.timer.start(1000)  # every 1 second
        self.event_box = QTextEdit(self)
        self.event_box.setGeometry(10, 400, 300, 150)
        self.event_box.setReadOnly(True)
        self.event_timer = QTimer()
        self.event_timer.timeout.connect(self.load_events)
        self.event_timer.start(1000)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        item = event.source().currentItem().text()

        # CREATE COMPONENT
        if item == "Pump":
            comp = DraggableComponent(
                "pump",
                "win_ui/assets/pump_off.png",
                "win_ui/assets/pump_on.png",
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

        # position + show
        comp.move(event.position().toPoint())
        comp.show()
        comp.tag = f"pump_{len(self.components)}"
        # store component
        self.components.append(comp)

        # register state AFTER creation
        self.tag_values[comp.id] = False  # ⚠️ ensure comp.id exists in your class

        print("Added:", comp.get_data())

    def get_all_components(self):
        return [c.get_data() for c in self.components]

    def update_tag(self, comp):
        if comp.tag:
            self.tag_values[comp.tag] = comp.state
            print("Updated:", self.tag_values)

    def sync_from_backend(self):
        try:
            res = requests.get("http://127.0.0.1:8000/state")
            data = res.json()

            for comp in self.components:
                if comp.tag in data:
                    new_state = data[comp.tag]

                    if comp.state != new_state:
                        comp.state = new_state
                        comp.update_image()

        except Exception as e:
            print("sync error:", e)

    def load_events(self):
        try:
            res = requests.get("http://127.0.0.1:8000/events")
            events = res.json()

            text = ""

            for e in events[-10:]:  # last  10 events
              text += f"[{e['type']}] {e['message']}\n"

            self.event_box.setText(text)

        except Exception as e:
            print("event sync error:", e)