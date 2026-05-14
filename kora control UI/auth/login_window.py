from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor

from core.role_manager import role_manager, Role


class LoginWindow(QWidget):
    login_successful = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KORA SCADA — Login")
        self.setFixedSize(480, 560)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._drag_pos = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_title_bar())

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setStyleSheet("""
            #LoginCard {
                background-color: #16213e;
                border: 1px solid #0f3460;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        logo = QLabel("⚙")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 48px; color: #00d4ff;")

        title = QLabel("KORA CONTROL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #00d4ff; letter-spacing: 4px;")

        subtitle = QLabel("SCADA SYSTEM")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 11px; color: #ffffff; letter-spacing: 8px;")

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #ADD8E6;")

        field_style = "font-size: 10px; color: #ffffff; letter-spacing: 2px;"

        user_lbl = QLabel("USERNAME")
        user_lbl.setStyleSheet(field_style)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFixedHeight(40)

        pass_lbl = QLabel("PASSWORD")
        pass_lbl.setStyleSheet(field_style)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.returnPressed.connect(self._attempt_login)

        role_lbl = QLabel("ROLE")
        role_lbl.setStyleSheet(field_style)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["operator", "admin", "viewer"])
        self.role_combo.setFixedHeight(40)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #ff4444; font-size: 12px;")
        self.error_label.setFixedHeight(20)

        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setFixedHeight(44)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self._attempt_login)

        footer = QLabel("Authorized Personnel Only")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("font-size: 10px; color: #444;")

        for w in [logo, title, subtitle, divider]:
            layout.addWidget(w)
        layout.addSpacing(8)
        for w in [user_lbl, self.username_input, pass_lbl, self.password_input,
                  role_lbl, self.role_combo, self.error_label, self.login_btn]:
            layout.addWidget(w)
        layout.addStretch()
        layout.addWidget(footer)

        root.addWidget(card)

    def _make_title_bar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet("background-color: #0f3460;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 8, 0)

        title = QLabel("KORA SCADA")
        title.setStyleSheet("color: #00d4ff; font-size: 11px; font-weight: bold; letter-spacing: 2px;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #888; font-size: 14px; }
            QPushButton:hover { color: #ff4444; }
        """)
        close_btn.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(close_btn)

        bar.mousePressEvent = self._title_mouse_press
        bar.mouseMoveEvent = self._title_mouse_move
        return bar

    def _title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def _attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role_str = self.role_combo.currentText()

        if not username or not password:
            self.error_label.setText("Username and password are required.")
            return

        role_map = {
            "admin":    Role.ADMIN,
            "operator": Role.OPERATOR,
            "viewer":   Role.VIEWER,
        }
        role_manager.set_user(username, role_map.get(role_str, Role.VIEWER))

        self.error_label.setText("")
        self.login_btn.setEnabled(False)
        self.login_btn.setText("AUTHENTICATING...")

        QTimer.singleShot(600, lambda: self._on_auth_success(username, role_str))

    def _on_auth_success(self, username: str, role: str):
        self.login_successful.emit(username, role)
        self.close()
