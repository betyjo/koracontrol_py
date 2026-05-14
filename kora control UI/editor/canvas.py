"""
HMI Canvas — the drop target where HMI items are placed and arranged.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen

from editor.hmi_item import HMIItem

GRID_SIZE = 20


class HMICanvas(QWidget):
    item_selected   = pyqtSignal(object)   # HMIItem or None
    item_dropped    = pyqtSignal(object)   # HMIItem
    layout_changed  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[HMIItem] = []
        self._selected_item: HMIItem | None = None
        self._show_grid = True
        self.setMinimumSize(900, 600)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #0d0d1a;")

    # --- Grid ---
    def set_grid_visible(self, visible: bool):
        self._show_grid = visible
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0d0d1a"))

        if self._show_grid:
            p.setPen(QPen(QColor("#1a1a2e"), 1))
            for x in range(0, self.width(), GRID_SIZE):
                p.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), GRID_SIZE):
                p.drawLine(0, y, self.width(), y)

    # --- Drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            component_type = event.mimeData().text()
            pos = event.position().toPoint()
            pos = self._snap(pos)
            self._create_item(component_type, pos.x(), pos.y())
            event.acceptProposedAction()
            self.layout_changed.emit()

    # --- Item management ---
    def _create_item(self, component_type: str, x: int, y: int,
                     tag: str = "", label: str = "") -> HMIItem:
        widget = self._make_widget(component_type, tag, label)
        item = HMIItem(component_type, widget, tag=tag, label=label, parent=self)
        item.move(x, y)
        item.show()
        item.selected_changed.connect(self._on_item_selected)
        item.moved.connect(lambda i: self.layout_changed.emit())
        self._items.append(item)
        self._select(item)
        return item

    def _make_widget(self, component_type: str,
                     tag: str = "", label: str = "") -> QWidget:
        from components.tank  import Tank
        from components.pump  import Pump
        from components.valve import Valve
        from components.gauge import Gauge
        from core.tag_engine  import tag_engine

        lbl = label or component_type.capitalize()
        if component_type == "tank":
            w = Tank(lbl, tag=tag or None)
            w.setFixedSize(90, 180)
        elif component_type == "pump":
            w = Pump(lbl, tag=tag or None)
            w.setFixedSize(100, 110)
        elif component_type == "valve":
            w = Valve(lbl, tag=tag or None)
            w.setFixedSize(90, 100)
        else:  # gauge
            w = Gauge(lbl, tag=tag or None, min_val=0, max_val=100, units="")
            w.setFixedSize(140, 140)

        if tag:
            w.bind(tag_engine)
        return w

    def _on_item_selected(self, item: HMIItem):
        if item.is_selected():
            # Deselect others
            for other in self._items:
                if other is not item and other.is_selected():
                    other.set_selected(False)
            self._selected_item = item
            self.item_selected.emit(item)
        else:
            if self._selected_item is item:
                self._selected_item = None
                self.item_selected.emit(None)

    def _select(self, item: HMIItem):
        for other in self._items:
            if other is not item:
                other.set_selected(False)
        item.set_selected(True)

    def mousePressEvent(self, event):
        # Click on empty canvas → deselect
        child = self.childAt(event.position().toPoint())
        if child is None or child is self:
            for item in self._items:
                item.set_selected(False)
            self._selected_item = None
            self.item_selected.emit(None)

    def delete_selected(self):
        if self._selected_item:
            self._selected_item.hide()
            self._selected_item.deleteLater()
            self._items.remove(self._selected_item)
            self._selected_item = None
            self.item_selected.emit(None)
            self.layout_changed.emit()

    def clear(self):
        for item in self._items:
            item.hide()
            item.deleteLater()
        self._items.clear()
        self._selected_item = None
        self.item_selected.emit(None)
        self.layout_changed.emit()

    # --- Snap to grid ---
    def _snap(self, pos):
        from PyQt6.QtCore import QPoint
        return QPoint(
            round(pos.x() / GRID_SIZE) * GRID_SIZE,
            round(pos.y() / GRID_SIZE) * GRID_SIZE,
        )

    # --- Serialization ---
    def to_layout(self) -> list[dict]:
        return [item.to_dict() for item in self._items]

    def load_layout(self, layout: list[dict]):
        self.clear()
        for entry in layout:
            self._create_item(
                entry["type"],
                entry.get("x", 0),
                entry.get("y", 0),
                tag=entry.get("tag", ""),
                label=entry.get("label", ""),
            )
        self.layout_changed.emit()
