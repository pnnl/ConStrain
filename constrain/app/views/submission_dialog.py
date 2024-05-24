from PyQt6 import QtWidgets


class SubmissionDialog(QtWidgets.QDialog):
    def __init__(self) -> None:
        """Creates a read-only popup containing the verbose run through Workflow"""
        super(SubmissionDialog, self).__init__()
        self.init_ui()

    def init_ui(self) -> None:
        self.setMinimumSize(400, 500)
        self.setWindowTitle("Results")
        self.layout = QtWidgets.QVBoxLayout()
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

    def update_text(self, message: str) -> None:
        self.text_edit.append(message)
