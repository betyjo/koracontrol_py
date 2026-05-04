from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class DraggableComponent(QLabel):
    def __init__(self, off_img, on_img, parent=None):
        super().__init__(parent)

        self.off_img = QPixmap(off_img)
        self.on_img = QPixmap(on_img)

        self.state = False  # OFF

        self.setPixmap(self.off_img)
        self.setScaledContents(True)
        self.resize(60, 60)

        self.dragging = False
        self.offset = None

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
        # toggle state
        self.state = not self.state
        self.update_image()

    def update_image(self):
        if self.state:
            self.setPixmap(self.on_img)
        else:
            self.setPixmap(self.off_img)