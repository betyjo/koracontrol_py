from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QFont

PALETTE_ITEMS = [
    ("tank",  "🛢  Tank",  "#00aaff"),
    ("pump",  "⚙  Pump",  "#00d4ff"),
    ("valve", "🔧  Valve", "#ffaa00"),
    ("gauge", "📊  Gauge", "#00ff88"),
]


class PaletteButton(QPushButton):
    def __init__(self, component_type: str, label: str, color: str, parent=None):
        super().__init__(label, parent)
        self.component_type = component_type
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #16213e; border: 1px solid {color};
                border-radius: 4px; color: {color};
                font-size: 13px; font-weight: bold;
                text-align: left; padding-left: 12px;
            }}
            QPushButton:hover {{ background-color: #1e3a5f; }}
        """)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.component_type)
            drag.setMimeData(mime)

            pix = QPixmap(120, 40)
            pix.fill(QColor("#16213e"))
            p = QPainter(pix)
            p.setPen(QColor("#00d4ff"))
            p.setFont(QFont("Segoe UI", 10))
            p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
            p.end()
            drag.setPixmap(pix)
            drag.setHotSpot(QPoint(60, 20))
            drag.exec(Qt.DropAction.CopyAction)


class ComponentPalette(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(160)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("COMPONENTS")
        title.setStyleSheet("font-size: 10px; color: #888; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #0f3460;")
        layout.addWidget(div)

        for ctype, label, color in PALETTE_ITEMS:
            layout.addWidget(PaletteButton(ctype, label, color))

        layout.addStretch()

        hint = QLabel("Drag onto canvas\nto place")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #444; font-size: 10px;")
        layout.addWidget(hint)
