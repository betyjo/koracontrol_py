from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont


class Tank(QWidget):
    def __init__(self, label: str = "TANK", tag: str = None, parent=None):
        super().__init__(parent)
        self._label = label
        self._tag = tag
        self._level = 0.0
        self._display_level = 0.0
        self._alarm_high = 0.85
        self._alarm_low = 0.15
        self.setMinimumSize(80, 160)

        self._anim = QPropertyAnimation(self, b"display_level")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def bind(self, tag_engine):
        tag_engine.tag_updated.connect(self._on_tag_update)

    def _on_tag_update(self, name: str, value):
        if name == self._tag:
            self.set_level(float(value))

    def get_display_level(self) -> float:
        return self._display_level

    def set_display_level(self, v: float):
        self._display_level = max(0.0, min(1.0, v))
        self.update()

    display_level = pyqtProperty(float, get_display_level, set_display_level)

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))
        self._anim.stop()
        self._anim.setStartValue(self._display_level)
        self._anim.setEndValue(self._level)
        self._anim.start()

    def get_level(self) -> float:
        return self._level

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin = 10
        label_h = 20
        tx = margin
        ty = margin
        tw = w - 2 * margin
        th = h - 2 * margin - label_h - 4

        p.setPen(QPen(QColor("#0f3460"), 2))
        p.setBrush(QColor("#0d0d1a"))
        p.drawRoundedRect(tx, ty, tw, th, 6, 6)

        fill_h = int(th * self._display_level)
        fill_y = ty + th - fill_h

        if self._display_level > 0.01:
            color = self._fill_color()
            grad = QLinearGradient(tx, fill_y, tx + tw, fill_y)
            grad.setColorAt(0, color.lighter(130))
            grad.setColorAt(1, color)
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.setClipRect(tx + 1, fill_y, tw - 2, fill_h)
            p.drawRoundedRect(tx + 1, ty + 1, tw - 2, th - 2, 5, 5)
            p.setClipping(False)

        p.setPen(QPen(QColor("#333"), 1))
        for i in range(1, 4):
            tick_y = ty + int(th * (1 - i / 4))
            p.drawLine(tx + tw - 8, tick_y, tx + tw - 2, tick_y)

        pct = int(self._display_level * 100)
        p.setPen(QColor("#e0e0e0"))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p.drawText(QRectF(tx, ty, tw, th), Qt.AlignmentFlag.AlignCenter, f"{pct}%")

        p.setPen(QColor("#00d4ff"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(QRectF(0, h - label_h, w, label_h), Qt.AlignmentFlag.AlignCenter, self._label)

    def _fill_color(self) -> QColor:
        if self._display_level >= self._alarm_high:
            return QColor("#ff4444")
        if self._display_level <= self._alarm_low:
            return QColor("#ffaa00")
        return QColor("#00aaff")
