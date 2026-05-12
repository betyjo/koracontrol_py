import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from canvas import Canvas
from sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SCADA Prototype")
        self.setGeometry(100, 100, 1000, 600)

        container = QWidget()
        layout = QHBoxLayout()

        self.sidebar = Sidebar()
        self.canvas = Canvas()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.canvas)

        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())