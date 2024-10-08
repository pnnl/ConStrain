from PyQt6.QtWidgets import QPushButton


class StandardButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setFixedSize(100, 30)
