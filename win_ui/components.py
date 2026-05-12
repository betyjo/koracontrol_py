import uuid
import requests
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtWidgets import QMenu, QInputDialog

class DraggableComponent(QLabel):
    def __init__(self, comp_type, off_img, on_img, parent=None):
        super().__init__(parent)
        
        self.tag = ""
        self.linked_tag = ""
        self.state = False

        self.id = str(uuid.uuid4())
        self.type = comp_type

        self.off_img = QPixmap(off_img)
        self.on_img = QPixmap(on_img)

        self.state = False

        self.setPixmap(self.off_img)
        self.setScaledContents(True)
        self.resize(60, 60)

        self.dragging = False
        self.offset = None
        self.tag = None   # NEW
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def mouseDoubleClickEvent(self, event):
        self.state = not self.state
        self.update_image()

    # 🔥 SEND TO BACKEND
        if self.tag:
         requests.post(
            "http://127.0.0.1:8000/set_tag",
            json={
                "tag": self.tag,
                "value": self.state
            }
        )

    def update_image(self):
        if self.state:
            self.setPixmap(self.on_img)
        else:
            self.setPixmap(self.off_img)

    def get_data(self):
        return {
            "id": self.id,
            "type": self.type,
            "x": self.x(),
            "y": self.y(),
            "state": self.state,
            "tag": self.tag
        }
    def set_tag(self, tag_name):
        self.tag = tag_name
    def contextMenuEvent(self, event):
        tag, ok = QInputDialog.getText(self, "Set Tag", "Enter tag name:")

        if ok and tag:
            self.set_tag(tag)
            print(f"{self.type} assigned tag: {tag}")
    

    def contextMenuEvent(self, event):

        menu = QMenu(self)

        set_tag_action = menu.addAction("Set Tag")
        set_link_action = menu.addAction("Set Linked Tank")

        action = menu.exec(event.globalPos())

        # -----------------------
        # SET DEVICE TAG
        # -----------------------

        if action == set_tag_action:
            text, ok = QInputDialog.getText(
                self,
                "Set Tag",
                "Enter tag:"
            )

            if ok:
                self.tag = text
                print("TAG:", self.tag)

        # -----------------------
        # SET LINKED DEVICE
        # -----------------------

        elif action == set_link_action:
            text, ok = QInputDialog.getText(
                self,
                "Set Linked Tank",
                "Enter linked tank tag:"
            )

            if ok:
                self.linked_tag = text
                print("LINK:", self.linked_tag)