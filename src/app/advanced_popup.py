from PyQt6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QPushButton,
    QDialog,
    QTextEdit,
    QMessageBox,
)
from PyQt6.QtGui import QFontMetricsF
import json


class AdvancedPopup(QDialog):
    def __init__(self, rect=None, edit=False):
        super().__init__()

        form_layout = QVBoxLayout()
        state_label = QLabel("State:")

        if edit:
            self.setWindowTitle("Edit State")
        else:
            self.setWindowTitle("Add State")

        self.state_input = QTextEdit()
        if rect:
            self.state_input.setText(rect.get_state_string())

        font = self.state_input.font()
        fontMetrics = QFontMetricsF(font)
        spaceWidth = fontMetrics.horizontalAdvance(" ")
        self.state_input.setTabStopDistance(spaceWidth * 4)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.check_state)

        form_layout.addWidget(state_label)
        form_layout.addWidget(self.state_input, 3)
        form_layout.addWidget(self.save_button)

        self.setLayout(form_layout)

    def get_state(self):
        state_text = self.state_input.toPlainText()

        try:
            state_json = json.loads(state_text)
        except json.decoder.JSONDecodeError:
            return None

        if state_json:
            if len(state_json.keys()) > 1:
                return None
            else:
                title = [key for key in state_json.keys()][0]
                state_json = state_json[title]
                state_json["Title"] = title
        return state_json

    def check_state(self):
        state = self.get_state()

        if not state:
            self.error_popup("Invalid state format")
        else:
            state_type = state.get("Type")

            if state_type not in ["Choice", "MethodCall"]:
                self.error_popup("Invalid type")
            elif state_type == "Choice" and "Choices" not in state.keys():
                self.error_popup("Choice type, but no Choices key")
            else:
                self.close()

    def error_popup(text):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Error in State")
        error_msg.setText(text)
        error_msg.exec()
