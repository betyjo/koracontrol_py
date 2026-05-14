from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
import datetime

from core.role_manager import role_manager
from core.tag_engine import tag_engine


class MainWindow(QMainWindow):
    def __init__(self, username: str, role: str):
        super().__init__()
        self.username = username
        self.role = role
        self.setWindowTitle("KORA SCADA — Dashboard")
        self.resize(1400, 860)
        self.setMinimumSize(1100, 700)
        self._build_ui()
        self._start_clock()
        tag_engine.start()
        tag_engine.tag_updated.connect(self._check_alarms)
        self._start_alarm_badge()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #1a1a2e;")
        root.addWidget(self.stack, 1)

        self._pages = {}
        self._add_overview()
        self._add_hmi_editor()
        self._add_alarm_screen()
        self._add_trend_screen()
        self._add_settings_screen()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("background-color: #0f3460; color: #00d4ff; font-size: 11px;")
        self._clock_label = QLabel()
        self.status_bar.addPermanentWidget(self._clock_label)
        self.status_bar.showMessage(f"  Logged in as: {self.username}  |  Role: {self.role.upper()}")

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("QFrame { background-color: #0f3460; border-right: 1px solid #00d4ff; }")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("⚙  KORA")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(60)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4ff; letter-spacing: 3px; border-bottom: 1px solid #1a1a2e;")
        layout.addWidget(header)

        nav_items = [
            ("overview", "🖥  Overview"),
            ("hmi",      "🔧  HMI Editor"),
            ("alarms",   "🔔  Alarms"),
            ("trends",   "📈  Trends"),
            ("settings", "⚙  Settings"),
        ]

        if not role_manager.has_permission("can_edit_hmi"):
            nav_items = [n for n in nav_items if n[0] != "hmi"]

        self._nav_buttons = {}
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setFixedHeight(48)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: #aaa; text-align: left;
                    padding-left: 20px; font-size: 13px;
                }
                QPushButton:hover { background-color: #1a1a2e; color: #fff; }
                QPushButton:checked { background-color: #1a1a2e; color: #00d4ff; border-left: 3px solid #00d4ff; }
            """)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            layout.addWidget(btn)
            self._nav_buttons[key] = btn

        layout.addStretch()

        user_label = QLabel(f"👤  {self.username}\n{self.role.upper()}")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label.setStyleSheet("color: #888; font-size: 11px; padding: 10px; border-top: 1px solid #1a1a2e;")
        layout.addWidget(user_label)

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedHeight(36)
        logout_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #ff4444; font-size: 12px; }
            QPushButton:hover { color: #ff6666; }
        """)
        logout_btn.clicked.connect(self._logout)
        layout.addWidget(logout_btn)

        return sidebar

    def _add_overview(self):
        from screens.overview_screen import OverviewScreen
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidget(OverviewScreen())
        self.stack.addWidget(scroll)
        self._pages["overview"] = self.stack.count() - 1

    def _add_hmi_editor(self):
        from editor.hmi_editor import HMIEditor
        self.stack.addWidget(HMIEditor())
        self._pages["hmi"] = self.stack.count() - 1

    def _add_alarm_screen(self):
        from screens.alarm_screen import AlarmScreen
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidget(AlarmScreen())
        self.stack.addWidget(scroll)
        self._pages["alarms"] = self.stack.count() - 1

    def _add_trend_screen(self):
        from screens.trend_screen import TrendScreen
        self.stack.addWidget(TrendScreen())
        self._pages["trends"] = self.stack.count() - 1

    def _add_settings_screen(self):
        from screens.settings_screen import SettingsScreen
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidget(SettingsScreen())
        self.stack.addWidget(scroll)
        self._pages["settings"] = self.stack.count() - 1

    def _navigate(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)
        if key in self._pages:
            self.stack.setCurrentIndex(self._pages[key])

    def _start_alarm_badge(self):
        from core.alarm_manager import alarm_manager
        def update_badge():
            count = alarm_manager.active_count()
            btn = self._nav_buttons.get("alarms")
            if btn:
                btn.setText(f"🔔  Alarms  ({count})" if count else "🔔  Alarms")
        alarm_manager.alarms_changed.connect(update_badge)
        update_badge()

    def _check_alarms(self, tag: str, value):
        from core.alarm_manager import alarm_manager, AlarmSeverity
        try:
            v = float(value)
        except (TypeError, ValueError):
            return
        rules = {
            "tank_a_level": [(0.9,  "Tank A critically high",     AlarmSeverity.CRITICAL),
                             (0.85, "Tank A high",                AlarmSeverity.HIGH)],
            "tank_b_level": [(0.9,  "Tank B critically high",     AlarmSeverity.CRITICAL)],
            "pressure":     [(8.5,  "Pressure critically high",   AlarmSeverity.CRITICAL),
                             (7.0,  "Pressure high",              AlarmSeverity.HIGH)],
            "temperature":  [(130,  "Temperature critically high", AlarmSeverity.CRITICAL),
                             (110,  "Temperature high",           AlarmSeverity.HIGH)],
        }
        for threshold, msg, sev in rules.get(tag, []):
            if v >= threshold:
                alarm_manager.raise_alarm(tag, msg, sev)
                break

    def _start_clock(self):
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self._clock_label.setText(f"{now}  ")

    def _logout(self):
        tag_engine.stop()
        role_manager.clear()
        from auth.login_window import LoginWindow
        self._login = LoginWindow()
        self._login.login_successful.connect(self._reopen)
        self._login.show()
        self.close()

    def _reopen(self, username: str, role: str):
        self._new_window = MainWindow(username, role)
        self._new_window.show()
        self._navigate("overview")
