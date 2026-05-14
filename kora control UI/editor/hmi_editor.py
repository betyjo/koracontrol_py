import json
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

from editor.palette import ComponentPalette
from editor.canvas import HMICanvas
from editor.properties_panel import PropertiesPanel

AUTOSAVE_PATH = "hmi_layout.json"


class HMIEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_autosave()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_toolbar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._palette = ComponentPalette()
        self._palette.setStyleSheet("background-color: #0f3460; border-right: 1px solid #1a1a2e;")
        body.addWidget(self._palette)

        self._canvas = HMICanvas()
        scroll = QScrollArea()
        scroll.setWidget(self._canvas)
        scroll.setWidgetResizable(False)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body.addWidget(scroll, 1)

        self._props = PropertiesPanel()
        self._props.setStyleSheet("background-color: #0f3460; border-left: 1px solid #1a1a2e;")
        body.addWidget(self._props)

        root.addLayout(body)

        self._canvas.item_selected.connect(self._on_item_selected)
        self._canvas.layout_changed.connect(self._autosave)
        self._props.delete_btn.clicked.connect(self._canvas.delete_selected)
        self._props.property_changed.connect(self._on_property_changed)

    def _build_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background-color: #0f3460; border-bottom: 1px solid #1a1a2e;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        title = QLabel("HMI EDITOR")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #00d4ff; letter-spacing: 2px;")
        layout.addWidget(title)
        layout.addStretch()

        self._grid_cb = QCheckBox("Grid")
        self._grid_cb.setChecked(True)
        self._grid_cb.toggled.connect(lambda v: self._canvas.set_grid_visible(v))
        layout.addWidget(self._grid_cb)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #1a1a2e;")
        layout.addWidget(sep)

        for label, slot in [("💾  Save", self._save_layout),
                             ("📂  Load", self._load_layout)]:
            btn = QPushButton(label)
            btn.setFixedWidth(90)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        clear_btn = QPushButton("🗑  Clear")
        clear_btn.setFixedWidth(90)
        clear_btn.setStyleSheet(
            "QPushButton { border-color: #ff4444; color: #ff4444; }"
            "QPushButton:hover { background-color: #ff4444; color: #1a1a2e; }"
        )
        clear_btn.clicked.connect(self._confirm_clear)
        layout.addWidget(clear_btn)

        return bar

    def _on_item_selected(self, item):
        self._props.load_item(item)
        if item:
            item.moved.connect(self._props.update_position)

    def _on_property_changed(self, item):
        w = item.inner_widget
        if hasattr(w, "_tag"):
            w._tag = item.tag
        self._autosave()

    def _save_layout(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save HMI Layout", AUTOSAVE_PATH, "JSON Files (*.json)")
        if path:
            self._write_layout(path)

    def _load_layout(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load HMI Layout", "", "JSON Files (*.json)")
        if path and os.path.exists(path):
            with open(path, "r") as f:
                self._canvas.load_layout(json.load(f))

    def _autosave(self):
        self._write_layout(AUTOSAVE_PATH)

    def _write_layout(self, path: str):
        try:
            with open(path, "w") as f:
                json.dump(self._canvas.to_layout(), f, indent=2)
        except Exception:
            pass

    def _load_autosave(self):
        if os.path.exists(AUTOSAVE_PATH):
            try:
                with open(AUTOSAVE_PATH, "r") as f:
                    self._canvas.load_layout(json.load(f))
            except Exception:
                pass

    def _confirm_clear(self):
        reply = QMessageBox.question(
            self, "Clear Canvas", "Remove all components from the canvas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._canvas.clear()
