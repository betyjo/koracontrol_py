from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFormLayout, QGroupBox,
    QFrame, QComboBox, QSpinBox, QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.role_manager import role_manager, Role, ROLE_PERMISSIONS


class SettingsScreen(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("SETTINGS")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4ff; letter-spacing: 3px;")
        root.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #0f3460; }
            QTabBar::tab { background: #0f3460; color: #888; padding: 8px 20px; border: none; }
            QTabBar::tab:selected { background: #16213e; color: #00d4ff; border-bottom: 2px solid #00d4ff; }
            QTabBar::tab:hover { color: #fff; }
        """)
        tabs.addTab(self._build_connection_tab(), "Connection")
        tabs.addTab(self._build_role_tab(),       "Roles & Permissions")
        tabs.addTab(self._build_display_tab(),    "Display")
        tabs.addTab(self._build_about_tab(),      "About")
        root.addWidget(tabs)

    def _build_connection_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        auth_box = QGroupBox("Backend Authentication API")
        auth_form = QFormLayout(auth_box)
        self.auth_host = QLineEdit("http://localhost")
        self.auth_port = QSpinBox()
        self.auth_port.setRange(1, 65535)
        self.auth_port.setValue(8000)
        self.auth_timeout = QSpinBox()
        self.auth_timeout.setRange(1, 60)
        self.auth_timeout.setValue(5)
        self.auth_timeout.setSuffix(" s")
        auth_form.addRow("Host:",    self.auth_host)
        auth_form.addRow("Port:",    self.auth_port)
        auth_form.addRow("Timeout:", self.auth_timeout)
        layout.addWidget(auth_box)

        comm_box = QGroupBox("Industrial Communication API")
        comm_form = QFormLayout(comm_box)
        self.comm_host = QLineEdit("opc.tcp://localhost")
        self.comm_port = QSpinBox()
        self.comm_port.setRange(1, 65535)
        self.comm_port.setValue(4840)
        self.comm_protocol = QComboBox()
        self.comm_protocol.addItems(["OPC-UA", "Modbus TCP", "MQTT", "REST"])
        self.comm_refresh = QSpinBox()
        self.comm_refresh.setRange(50, 5000)
        self.comm_refresh.setValue(200)
        self.comm_refresh.setSuffix(" ms")
        comm_form.addRow("Host:",         self.comm_host)
        comm_form.addRow("Port:",         self.comm_port)
        comm_form.addRow("Protocol:",     self.comm_protocol)
        comm_form.addRow("Refresh rate:", self.comm_refresh)
        layout.addWidget(comm_box)

        btn_row = QHBoxLayout()
        test_auth_btn = QPushButton("Test Auth Connection")
        test_auth_btn.clicked.connect(lambda: self._test_connection("auth"))
        test_comm_btn = QPushButton("Test Comm Connection")
        test_comm_btn.clicked.connect(lambda: self._test_connection("comm"))
        btn_row.addWidget(test_auth_btn)
        btn_row.addWidget(test_comm_btn)
        layout.addLayout(btn_row)

        self._conn_status = QLabel("")
        self._conn_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._conn_status)

        save_btn = QPushButton("Save Connection Settings")
        save_btn.clicked.connect(self._save_connection)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def _test_connection(self, target: str):
        self._conn_status.setText(f"⚠  {target.upper()} API not reachable (connect your API here)")
        self._conn_status.setStyleSheet("color: #ffaa00; font-size: 12px;")

    def _save_connection(self):
        self._conn_status.setText("✔  Settings saved (restart to apply)")
        self._conn_status.setStyleSheet("color: #00ff88; font-size: 12px;")

    def _build_role_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        user_box = QGroupBox("Current Session")
        user_form = QFormLayout(user_box)
        user_lbl = QLabel(role_manager.current_user or "—")
        user_lbl.setStyleSheet("color: #00d4ff; font-weight: bold;")
        role_lbl = QLabel(role_manager.current_role.value.upper() if role_manager.current_role else "—")
        role_lbl.setStyleSheet("color: #00ff88; font-weight: bold;")
        user_form.addRow("Username:", user_lbl)
        user_form.addRow("Role:",     role_lbl)
        layout.addWidget(user_box)

        perm_box = QGroupBox("Role Permission Matrix")
        perm_layout = QVBoxLayout(perm_box)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("Permission"), 3)
        for role in Role:
            lbl = QLabel(role.value.upper())
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #00d4ff; font-weight: bold; font-size: 11px;")
            header_row.addWidget(lbl, 1)
        perm_layout.addLayout(header_row)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #0f3460;")
        perm_layout.addWidget(div)

        for perm in list(next(iter(ROLE_PERMISSIONS.values())).keys()):
            row = QHBoxLayout()
            lbl = QLabel(perm.replace("_", " ").title())
            lbl.setStyleSheet("color: #aaa; font-size: 12px;")
            row.addWidget(lbl, 3)
            for role in Role:
                has = ROLE_PERMISSIONS[role].get(perm, False)
                icon = QLabel("✔" if has else "✘")
                icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon.setStyleSheet(f"color: {'#00ff88' if has else '#ff4444'}; font-size: 14px;")
                row.addWidget(icon, 1)
            perm_layout.addLayout(row)

        layout.addWidget(perm_box)
        layout.addStretch()
        return w

    def _build_display_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        box = QGroupBox("Display Preferences")
        form = QFormLayout(box)

        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(50, 2000)
        self.refresh_spin.setValue(200)
        self.refresh_spin.setSuffix(" ms")

        self.anim_cb  = QCheckBox("Enable component animations")
        self.anim_cb.setChecked(True)
        self.grid_cb  = QCheckBox("Show grid in HMI editor")
        self.grid_cb.setChecked(True)
        self.blink_cb = QCheckBox("Blink critical alarms")
        self.blink_cb.setChecked(True)

        form.addRow("UI refresh rate:", self.refresh_spin)
        form.addRow("", self.anim_cb)
        form.addRow("", self.grid_cb)
        form.addRow("", self.blink_cb)
        layout.addWidget(box)

        save_btn = QPushButton("Apply Display Settings")
        save_btn.clicked.connect(self._apply_display)
        layout.addWidget(save_btn)

        self._disp_status = QLabel("")
        self._disp_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._disp_status)
        layout.addStretch()
        return w

    def _apply_display(self):
        from core.tag_engine import tag_engine
        tag_engine._refresh_ms = self.refresh_spin.value()
        self._disp_status.setText("✔  Display settings applied")
        self._disp_status.setStyleSheet("color: #00ff88; font-size: 12px;")

    def _build_about_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        for text, style in [
            ("⚙",              "font-size: 64px; color: #00d4ff;"),
            ("KORA CONTROL",   "font-size: 24px; font-weight: bold; color: #00d4ff; letter-spacing: 4px;"),
            ("SCADA SYSTEM",   "font-size: 12px; color: #888; letter-spacing: 6px;"),
        ]:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(style)
            layout.addWidget(lbl)

        layout.addSpacing(16)

        for line, color in [
            ("Version 1.0.0",             "#e0e0e0"),
            ("Built with Python + PyQt6", "#888"),
            ("Real-time refresh ≤ 200ms", "#888"),
            ("Dark industrial theme",     "#888"),
        ]:
            lbl = QLabel(line)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
            layout.addWidget(lbl)

        layout.addStretch()
        return w
