import sys
from PyQt6.QtWidgets import QApplication


def load_theme(app: QApplication):
    try:
        with open("theme/dark_theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("KORA SCADA")
    app.setOrganizationName("Kora Control")

    load_theme(app)

    from auth.login_window import LoginWindow
    from dashboard.main_window import MainWindow

    login = LoginWindow()

    def on_login(username: str, role: str):
        window = MainWindow(username, role)
        window.show()
        window._navigate("overview")
        window._nav_buttons.get("overview") and window._nav_buttons["overview"].setChecked(True)

    login.login_successful.connect(on_login)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
