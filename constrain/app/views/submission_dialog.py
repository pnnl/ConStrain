from PyQt6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QTextEdit,
)


class SubmissionDialog(QDialog):
    def __init__(self):
        """Creates a read-only popup containing the verbose run through Workflow"""
        super(SubmissionDialog, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(400, 500)
        self.setWindowTitle("Results")
        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

    def update_text(self, message):
        self.text_edit.append(message)
