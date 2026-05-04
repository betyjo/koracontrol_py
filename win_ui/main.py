import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SCADA Prototype")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())