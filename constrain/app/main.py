import sys

from PyQt6.QtWidgets import QApplication

from constrain.app.views.main_window import MainWindow


def open():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    open()
