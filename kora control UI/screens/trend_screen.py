from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from collections import deque
import time

try:
    import pyqtgraph as pg
    import numpy as np
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

from core.tag_engine import tag_engine

TREND_TAGS = {
    "pressure":     {"label": "Pressure",     "color": "#00d4ff", "unit": "bar"},
    "temperature":  {"label": "Temperature",  "color": "#ff8800", "unit": "°C"},
    "flow_rate":    {"label": "Flow Rate",    "color": "#00ff88", "unit": "L/min"},
    "tank_a_level": {"label": "Tank A Level", "color": "#aa88ff", "unit": "%"},
    "tank_b_level": {"label": "Tank B Level", "color": "#ff88aa", "unit": "%"},
}

HISTORY_SECONDS = 120
SAMPLE_RATE_MS  = 200


class TrendScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffers: dict[str, deque] = {
            tag: deque(maxlen=int(HISTORY_SECONDS * 1000 / SAMPLE_RATE_MS))
            for tag in TREND_TAGS
        }
        self._active_tags: set[str] = {"pressure", "temperature", "flow_rate"}
        self._paused = False
        self._build_ui()
        tag_engine.tag_updated.connect(self._on_tag_update)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("TREND CHARTS")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4ff; letter-spacing: 3px;")
        header_row.addWidget(title)
        header_row.addStretch()

        self.pause_btn = QPushButton("⏸  PAUSE")
        self.pause_btn.setFixedWidth(110)
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(self._toggle_pause)
        header_row.addWidget(self.pause_btn)

        self.clear_btn = QPushButton("🗑  CLEAR")
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.clicked.connect(self._clear_history)
        header_row.addWidget(self.clear_btn)
        root.addLayout(header_row)

        selector_box = QGroupBox("Visible Tags")
        selector_layout = QHBoxLayout(selector_box)
        self._checkboxes: dict[str, QCheckBox] = {}
        for tag, meta in TREND_TAGS.items():
            cb = QCheckBox(meta["label"])
            cb.setChecked(tag in self._active_tags)
            cb.setStyleSheet(f"color: {meta['color']}; font-weight: bold;")
            cb.toggled.connect(lambda checked, t=tag: self._toggle_tag(t, checked))
            selector_layout.addWidget(cb)
            self._checkboxes[tag] = cb
        selector_layout.addStretch()
        root.addWidget(selector_box)

        if HAS_PYQTGRAPH:
            self._build_chart(root)
        else:
            fallback = QLabel("pyqtgraph not installed.\nRun: pip install pyqtgraph")
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback.setStyleSheet("color: #ff4444; font-size: 14px;")
            root.addWidget(fallback)

    def _build_chart(self, root: QVBoxLayout):
        pg.setConfigOption("background", "#16213e")
        pg.setConfigOption("foreground", "#e0e0e0")

        self._plot = pg.PlotWidget()
        self._plot.setLabel("bottom", "Time", units="s ago")
        self._plot.setLabel("left", "Value")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.addLegend(offset=(10, 10))
        self._plot.setMouseEnabled(x=True, y=True)
        self._plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._plot.getAxis("bottom").setPen(pg.mkPen("#0f3460"))
        self._plot.getAxis("left").setPen(pg.mkPen("#0f3460"))

        self._curves: dict[str, pg.PlotDataItem] = {}
        for tag, meta in TREND_TAGS.items():
            curve = self._plot.plot([], [],
                name=f"{meta['label']} ({meta['unit']})",
                pen=pg.mkPen(color=meta["color"], width=2))
            curve.setVisible(tag in self._active_tags)
            self._curves[tag] = curve

        root.addWidget(self._plot)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._update_plot)
        self._refresh_timer.start(200)

    def _on_tag_update(self, name: str, value):
        if name in self._buffers and not self._paused:
            try:
                self._buffers[name].append((time.monotonic(), float(value)))
            except (TypeError, ValueError):
                pass

    def _update_plot(self):
        if not HAS_PYQTGRAPH or self._paused:
            return
        now = time.monotonic()
        for tag, curve in self._curves.items():
            buf = self._buffers[tag]
            if not buf:
                continue
            times  = np.array([t for t, _ in buf])
            values = np.array([v for _, v in buf])
            curve.setData(times - now, values)

    def _toggle_tag(self, tag: str, visible: bool):
        if visible:
            self._active_tags.add(tag)
        else:
            self._active_tags.discard(tag)
        if HAS_PYQTGRAPH and tag in self._curves:
            self._curves[tag].setVisible(visible)

    def _toggle_pause(self, paused: bool):
        self._paused = paused
        self.pause_btn.setText("▶  RESUME" if paused else "⏸  PAUSE")

    def _clear_history(self):
        for buf in self._buffers.values():
            buf.clear()
        if HAS_PYQTGRAPH:
            for curve in self._curves.values():
                curve.setData([], [])
