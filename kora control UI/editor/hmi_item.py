from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen


class HMIItem(QFrame):
    selected_changed = pyqtSignal(object)
    moved            = pyqtSignal(object)

    def __init__(self, component_type: str, widget: QWidget,
                 tag: str = "", label: str = "", parent=None):
        super().__init__(parent)
        self.component_type = component_type
        self.tag = tag
        self.label = label
        self._selected = False
        self._drag_offset = QPoint()

        self.setFixedSize(widget.minimumWidth() + 16, widget.minimumHeight() + 16)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setStyleSheet("QFrame { border: none; background: transparent; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(widget)
        self._widget = widget

    @property
    def inner_widget(self) -> QWidget:
        return self._widget

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update()
        self.selected_changed.emit(self)

    def is_selected(self) -> bool:
        return self._selected

    def to_dict(self) -> dict:
        return {
            "type":  self.component_type,
            "tag":   self.tag,
            "label": self.label,
            "x":     self.x(),
            "y":     self.y(),
        }

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.position().toPoint()
            self.set_selected(True)
            self.raise_()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = self.mapToParent(event.position().toPoint() - self._drag_offset)
            parent = self.parentWidget()
            if parent:
                new_pos.setX(max(0, min(new_pos.x(), parent.width()  - self.width())))
                new_pos.setY(max(0, min(new_pos.y(), parent.height() - self.height())))
            self.move(new_pos)
            self.moved.emit(self)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._selected:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(QPen(QColor("#00d4ff"), 2, Qt.PenStyle.DashLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(1, 1, self.width() - 2, self.height() - 2)
            p.setBrush(QColor("#00d4ff"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(self.width() - 8, self.height() - 8, 7, 7)
