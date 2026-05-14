from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QFrame, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from core.alarm_manager import alarm_manager, AlarmSeverity, AlarmState, Alarm
from core.role_manager import role_manager

SEVERITY_COLORS = {
    AlarmSeverity.CRITICAL: "#3a0000",
    AlarmSeverity.HIGH:     "#2a1500",
    AlarmSeverity.MEDIUM:   "#1a1a00",
    AlarmSeverity.LOW:      "#001a1a",
}

SEVERITY_TEXT = {
    AlarmSeverity.CRITICAL: "#ff4444",
    AlarmSeverity.HIGH:     "#ff8800",
    AlarmSeverity.MEDIUM:   "#ffdd00",
    AlarmSeverity.LOW:      "#00d4ff",
}

HEADERS = ["Timestamp", "Severity", "Tag", "Message", "State", "Ack By"]


class AlarmScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter = "ALL"
        self._build_ui()
        alarm_manager.alarms_changed.connect(self._refresh)
        self._seed_demo_alarms()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("ALARM MANAGEMENT")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff4444; letter-spacing: 3px;")
        header_row.addWidget(title)
        header_row.addStretch()
        self.count_label = QLabel("● 0 ACTIVE")
        self.count_label.setStyleSheet("font-size: 13px; color: #ff4444; font-weight: bold;")
        header_row.addWidget(self.count_label)
        root.addLayout(header_row)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "ACTIVE", "ACK", "CLEARED", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.filter_combo.setFixedWidth(120)
        self.filter_combo.currentTextChanged.connect(self._on_filter_change)
        toolbar.addWidget(self.filter_combo)
        toolbar.addStretch()

        if role_manager.has_permission("can_acknowledge_alarms"):
            self.ack_btn = QPushButton("ACK SELECTED")
            self.ack_btn.setFixedWidth(140)
            self.ack_btn.clicked.connect(self._ack_selected)
            toolbar.addWidget(self.ack_btn)

            self.ack_all_btn = QPushButton("ACK ALL")
            self.ack_all_btn.setFixedWidth(100)
            self.ack_all_btn.setStyleSheet(
                "QPushButton { border-color: #ff8800; color: #ff8800; }"
                "QPushButton:hover { background-color: #ff8800; color: #1a1a2e; }"
            )
            self.ack_all_btn.clicked.connect(self._ack_all)
            toolbar.addWidget(self.ack_all_btn)

        root.addLayout(toolbar)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #0f3460;")
        root.addWidget(div)

        self.table = QTableWidget()
        self.table.setColumnCount(len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #16213e; border: 1px solid #0f3460; gridline-color: #0f3460; }
            QTableWidget::item:selected { background-color: #1e3a5f; }
            QHeaderView::section { background-color: #0f3460; color: #00d4ff; padding: 6px; border: none; font-weight: bold; }
        """)
        root.addWidget(self.table)

        self._blink_state = False
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink)
        self._blink_timer.start(800)

    def _on_filter_change(self, text: str):
        self._filter = text
        self._refresh()

    def _get_filtered_alarms(self) -> list[Alarm]:
        all_alarms = alarm_manager.all_alarms()
        f = self._filter
        if f == "ALL":
            return all_alarms
        state_map = {"ACTIVE": AlarmState.ACTIVE, "ACK": AlarmState.ACKNOWLEDGED, "CLEARED": AlarmState.CLEARED}
        if f in state_map:
            return [a for a in all_alarms if a.state == state_map[f]]
        sev_map = {s.value: s for s in AlarmSeverity}
        if f in sev_map:
            return [a for a in all_alarms if a.severity == sev_map[f]]
        return all_alarms

    def _refresh(self):
        alarms = self._get_filtered_alarms()
        self.table.setRowCount(len(alarms))
        for row, alarm in enumerate(alarms):
            for col, text in enumerate(alarm.to_row()):
                item = QTableWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, alarm.id)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(SEVERITY_COLORS.get(alarm.severity, "#16213e")))
                if col == 1:
                    item.setForeground(QColor(SEVERITY_TEXT.get(alarm.severity, "#e0e0e0")))
                    item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                if col == 4:
                    item.setForeground(QColor(
                        "#ff4444" if alarm.state == AlarmState.ACTIVE else
                        "#ffaa00" if alarm.state == AlarmState.ACKNOWLEDGED else "#00ff88"
                    ))
                self.table.setItem(row, col, item)

        count = alarm_manager.active_count()
        self.count_label.setText(f"● {count} ACTIVE")
        self.count_label.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {'#ff4444' if count > 0 else '#00ff88'};"
        )

    def _blink(self):
        self._blink_state = not self._blink_state
        for row in range(self.table.rowCount()):
            state_item = self.table.item(row, 4)
            if state_item and state_item.text() == "ACTIVE":
                for col in range(self.table.columnCount()):
                    cell = self.table.item(row, col)
                    if cell:
                        alarm_id = cell.data(Qt.ItemDataRole.UserRole)
                        alarm = next((a for a in alarm_manager.all_alarms() if a.id == alarm_id), None)
                        if alarm:
                            base = QColor(SEVERITY_COLORS.get(alarm.severity, "#16213e"))
                            if self._blink_state and alarm.severity == AlarmSeverity.CRITICAL:
                                cell.setBackground(QColor("#5a0000"))
                            else:
                                cell.setBackground(base)

    def _ack_selected(self):
        ids_seen = set()
        for item in self.table.selectedItems():
            alarm_id = item.data(Qt.ItemDataRole.UserRole)
            if alarm_id not in ids_seen:
                ids_seen.add(alarm_id)
                alarm_manager.acknowledge(alarm_id, role_manager.current_user or "operator")

    def _ack_all(self):
        alarm_manager.acknowledge_all(role_manager.current_user or "operator")

    def _seed_demo_alarms(self):
        alarm_manager.raise_alarm("tank_a_level",   "Tank A level critically high", AlarmSeverity.CRITICAL)
        alarm_manager.raise_alarm("pump_1_running", "Pump 1 unexpected stop",       AlarmSeverity.HIGH)
        alarm_manager.raise_alarm("pressure",       "Pressure above setpoint",      AlarmSeverity.MEDIUM)
        alarm_manager.raise_alarm("temperature",    "Temperature sensor drift",     AlarmSeverity.LOW)
