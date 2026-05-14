from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF
import math


class Pump(QWidget):
    def __init__(self, label: str = "PUMP", tag: str = None, parent=None):
        super().__init__(parent)
        self._label = label
        self._tag = tag
        self._running = False
        self._angle = 0.0
        self.setMinimumSize(90, 110)

        self._spin_timer = QTimer(self)
        self._spin_timer.timeout.connect(self._tick)

    def bind(self, tag_engine):
        tag_engine.tag_updated.connect(self._on_tag_update)

    def _on_tag_update(self, name: str, value):
        if name == self._tag:
            self.set_running(bool(value))

    def set_running(self, running: bool):
        self._running = running
        if running:
            self._spin_timer.start(30)
        else:
            self._spin_timer.stop()
            self.update()

    def is_running(self) -> bool:
        return self._running

    def _tick(self):
        self._angle = (self._angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        label_h = 20
        cx = w // 2
        cy = (h - label_h) // 2
        r = min(cx, cy) - 8

        p.setBrush(QColor("#1e3a5f") if self._running else QColor("#1a1a2e"))
        p.setPen(QPen(QColor("#0f3460"), 2))
        p.drawEllipse(QPointF(cx, cy), r, r)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#00d4ff") if self._running else QColor("#555"))
        p.save()
        p.translate(cx, cy)
        p.rotate(self._angle)
        for i in range(4):
            p.save()
            p.rotate(i * 90)
            blade = QPolygonF([
                QPointF(0, 0),
                QPointF(r * 0.35, -r * 0.15),
                QPointF(r * 0.75, -r * 0.08),
                QPointF(r * 0.75,  r * 0.08),
                QPointF(r * 0.35,  r * 0.15),
            ])
            p.drawPolygon(blade)
            p.restore()
        p.restore()

        p.setBrush(QColor("#00d4ff") if self._running else QColor("#444"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), r * 0.18, r * 0.18)

        p.setPen(QPen(QColor("#00ff88") if self._running else QColor("#ff4444"), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r + 4, r + 4)

        status = "RUN" if self._running else "STOP"
        p.setPen(QColor("#00d4ff"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(QRectF(0, h - label_h, w, label_h),
                   Qt.AlignmentFlag.AlignCenter, f"{self._label}  [{status}]")
