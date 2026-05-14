from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF


class Valve(QWidget):
    def __init__(self, label: str = "VALVE", tag: str = None, parent=None):
        super().__init__(parent)
        self._label = label
        self._tag = tag
        self._position = 0.0
        self._display_pos = 0.0
        self.setMinimumSize(80, 100)

        self._anim = QPropertyAnimation(self, b"display_pos")
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def bind(self, tag_engine):
        tag_engine.tag_updated.connect(self._on_tag_update)

    def _on_tag_update(self, name: str, value):
        if name == self._tag:
            v = float(value) if not isinstance(value, bool) else (1.0 if value else 0.0)
            self.set_position(v)

    def get_display_pos(self) -> float:
        return self._display_pos

    def set_display_pos(self, v: float):
        self._display_pos = max(0.0, min(1.0, v))
        self.update()

    display_pos = pyqtProperty(float, get_display_pos, set_display_pos)

    def set_position(self, pos: float):
        self._position = max(0.0, min(1.0, pos))
        self._anim.stop()
        self._anim.setStartValue(self._display_pos)
        self._anim.setEndValue(self._position)
        self._anim.start()

    def get_position(self) -> float:
        return self._position

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        label_h = 20
        cx = w // 2
        cy = (h - label_h) // 2
        r = min(cx, cy) - 10
        open_frac = self._display_pos

        pipe_h = int(r * 0.4)
        p.setBrush(QColor("#0f3460"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(0, cy - pipe_h // 2, cx - r + 2, pipe_h)
        p.drawRect(cx + r - 2, cy - pipe_h // 2, cx - r + 2, pipe_h)

        p.setBrush(QColor("#1e3a5f"))
        p.setPen(QPen(QColor("#0f3460"), 2))
        p.drawPolygon(QPolygonF([
            QPointF(cx - r, cy - r * 0.7),
            QPointF(cx - r, cy + r * 0.7),
            QPointF(cx, cy),
        ]))
        p.drawPolygon(QPolygonF([
            QPointF(cx + r, cy - r * 0.7),
            QPointF(cx + r, cy + r * 0.7),
            QPointF(cx, cy),
        ]))

        gate_y = cy - int(open_frac * r * 1.2)
        gate_w = int(r * 0.25)
        gate_h = int(r * 0.9)
        p.setBrush(QColor("#00d4ff") if open_frac > 0.05 else QColor("#ff4444"))
        p.setPen(QPen(QColor("#003355"), 1))
        p.drawRect(cx - gate_w // 2, gate_y - gate_h // 2, gate_w, gate_h)

        p.setPen(QPen(QColor("#888"), 1))
        p.drawLine(cx, gate_y - gate_h // 2, cx, cy - r - 4)

        if open_frac >= 0.99:
            status, sc = "OPEN", QColor("#00ff88")
        elif open_frac <= 0.01:
            status, sc = "CLOSED", QColor("#ff4444")
        else:
            status, sc = f"{int(open_frac * 100)}%", QColor("#ffaa00")

        p.setPen(sc)
        p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        p.drawText(QRectF(cx - 20, cy - 10, 40, 20), Qt.AlignmentFlag.AlignCenter, status)

        p.setPen(QColor("#00d4ff"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(QRectF(0, h - label_h, w, label_h), Qt.AlignmentFlag.AlignCenter, self._label)
