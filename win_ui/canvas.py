from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from components import DraggableComponent


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # create pump at click position
            pump = DraggableComponent(
                "ui/assets/pump_off.png",
                "ui/assets/pump_on.png",
                self
            )

            pump.move(event.pos())
            pump.show()