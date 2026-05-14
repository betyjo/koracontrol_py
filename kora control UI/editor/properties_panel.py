from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from editor.hmi_item import HMIItem


class PropertiesPanel(QWidget):
    property_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self._current_item: HMIItem | None = None
        self._build_ui()
        self._set_enabled(False)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("PROPERTIES")
        title.setStyleSheet("font-size: 10px; color: #888; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #0f3460;")
        layout.addWidget(div)

        self.type_label = QLabel("—")
        self.type_label.setStyleSheet("color: #00d4ff; font-weight: bold;")

        form = QFormLayout()
        form.setSpacing(8)

        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Display label")
        self.label_edit.textChanged.connect(self._on_label_changed)

        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("e.g. tank_a_level")
        self.tag_edit.textChanged.connect(self._on_tag_changed)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 2000)
        self.x_spin.valueChanged.connect(self._on_pos_changed)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 2000)
        self.y_spin.valueChanged.connect(self._on_pos_changed)

        form.addRow("Type:",  self.type_label)
        form.addRow("Label:", self.label_edit)
        form.addRow("Tag:",   self.tag_edit)
        form.addRow("X:",     self.x_spin)
        form.addRow("Y:",     self.y_spin)
        layout.addLayout(form)

        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet("color: #0f3460;")
        layout.addWidget(div2)

        self.delete_btn = QPushButton("🗑  Delete")
        self.delete_btn.setStyleSheet(
            "QPushButton { border-color: #ff4444; color: #ff4444; }"
            "QPushButton:hover { background-color: #ff4444; color: #1a1a2e; }"
        )
        layout.addWidget(self.delete_btn)
        layout.addStretch()

        hint_title = QLabel("AVAILABLE TAGS")
        hint_title.setStyleSheet("font-size: 9px; color: #555; letter-spacing: 1px;")
        layout.addWidget(hint_title)

        for t in ["tank_a_level", "tank_b_level", "pressure", "temperature",
                  "flow_rate", "pump_1_running", "pump_2_running",
                  "valve_inlet", "valve_outlet"]:
            lbl = QLabel(t)
            lbl.setStyleSheet("color: #444; font-size: 10px; font-family: monospace;")
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda e, tag=t: self.tag_edit.setText(tag)
            layout.addWidget(lbl)

    def load_item(self, item: HMIItem | None):
        self._current_item = item
        if item is None:
            self._set_enabled(False)
            self.type_label.setText("—")
            self.label_edit.clear()
            self.tag_edit.clear()
            return

        self._set_enabled(True)
        self.type_label.setText(item.component_type.upper())
        for widget, value in [
            (self.label_edit, item.label),
            (self.tag_edit,   item.tag),
        ]:
            widget.blockSignals(True)
            widget.setText(value)
            widget.blockSignals(False)
        for spin, value in [(self.x_spin, item.x()), (self.y_spin, item.y())]:
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)

    def update_position(self, item: HMIItem):
        if item is self._current_item:
            for spin, value in [(self.x_spin, item.x()), (self.y_spin, item.y())]:
                spin.blockSignals(True)
                spin.setValue(value)
                spin.blockSignals(False)

    def _on_label_changed(self, text: str):
        if self._current_item:
            self._current_item.label = text
            self.property_changed.emit(self._current_item)

    def _on_tag_changed(self, text: str):
        if self._current_item:
            self._current_item.tag = text
            self.property_changed.emit(self._current_item)

    def _on_pos_changed(self):
        if self._current_item:
            self._current_item.move(self.x_spin.value(), self.y_spin.value())

    def _set_enabled(self, enabled: bool):
        for w in [self.label_edit, self.tag_edit, self.x_spin, self.y_spin, self.delete_btn]:
            w.setEnabled(enabled)
