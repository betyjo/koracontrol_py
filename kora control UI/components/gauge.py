from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import math


class Gauge(QWidget):
    def __init__(self, label: str = "GAUGE", tag: str = None,
                 min_val: float = 0, max_val: float = 100,
                 units: str = "", parent=None):
        super().__init__(parent)
        self._label = label
        self._tag = tag
        self._min = min_val
        self._max = max_val
        self._units = units
        self._value = min_val
        self._display_value = float(min_val)
        self.setMinimumSize(120, 120)

        self._anim = QPropertyAnimation(self, b"display_value")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def bind(self, tag_engine):
        tag_engine.tag_updated.connect(self._on_tag_update)

    def _on_tag_update(self, name: str, value):
        if name == self._tag:
            self.set_value(float(value))

    def get_display_value(self) -> float:
        return self._display_value

    def set_display_value(self, v: float):
        self._display_value = v
        self.update()

    display_value = pyqtProperty(float, get_display_value, set_display_value)

    def set_value(self, value: float):
        self._value = max(self._min, min(self._max, value))
        self._anim.stop()
        self._anim.setStartValue(self._display_value)
        self._anim.setEndValue(self._value)
        self._anim.start()

    def get_value(self) -> float:
        return self._value

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        label_h = 22
        size = min(w, h - label_h) - 10
        cx = w // 2
        cy = (h - label_h) // 2
        arc_rect = QRectF(cx - size / 2, cy - size / 2, size, size)
        start_angle = 225
        span = 270

        p.setPen(QPen(QColor("#0f3460"), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(arc_rect, start_angle * 16, -span * 16)

        frac = max(0.0, min(1.0, (self._display_value - self._min) / max(self._max - self._min, 1e-9)))
        value_span = frac * span
        p.setPen(QPen(self._arc_color(frac), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(arc_rect, start_angle * 16, -int(value_span * 16))

        needle_rad = math.radians(start_angle - value_span)
        needle_len = size * 0.38
        nx = cx + needle_len * math.cos(needle_rad)
        ny = cy - needle_len * math.sin(needle_rad)
        p.setPen(QPen(QColor("#ffffff"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx, cy), QPointF(nx, ny))

        p.setBrush(QColor("#00d4ff"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), 5, 5)

        p.setPen(QColor("#e0e0e0"))
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.drawText(QRectF(cx - 40, cy + size * 0.1, 80, 24),
                   Qt.AlignmentFlag.AlignCenter, f"{self._display_value:.1f}")

        p.setPen(QColor("#888"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(QRectF(cx - 30, cy + size * 0.1 + 20, 60, 16),
                   Qt.AlignmentFlag.AlignCenter, self._units)

        p.setPen(QColor("#555"))
        p.setFont(QFont("Segoe UI", 7))
        tick_r = size * 0.52
        for angle, val in [(start_angle, self._min), (start_angle - span, self._max)]:
            rad = math.radians(angle)
            p.drawText(
                QRectF(cx + tick_r * math.cos(rad) - 15, cy - tick_r * math.sin(rad) - 8, 30, 16),
                Qt.AlignmentFlag.AlignCenter, str(int(val))
            )

        p.setPen(QColor("#00d4ff"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(QRectF(0, h - label_h, w, label_h), Qt.AlignmentFlag.AlignCenter, self._label)

    def _arc_color(self, frac: float) -> QColor:
        if frac >= 0.85:
            return QColor("#ff4444")
        if frac <= 0.10:
            return QColor("#ffaa00")
        return QColor("#00d4ff")
