import sys
import warnings

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QTextEdit,
)
from PyQt6.QtCore import QThread, pyqtSignal

from constrain.api.workflow import Workflow


class Worker(QThread):
    update_text = pyqtSignal(str)

    def __init__(self, json_data):
        """Given the finalized workflow, creates a thread that runs the workflow in the Workflow API

        Args:
            json_data (dict): The finalized, json formatted dict of information from each tab
        """
        super(Worker, self).__init__()
        self.json_data = json_data

    def run(self):
        """Runs the thread"""

        # captures sys.stdout in an EmittingStream object to display in a popup
        sys.stdout = EmittingStream(self.update_text)

        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=ResourceWarning)

        # creates and runs the workflow based on the workflow provided
        wf = Workflow(self.json_data)
        wf.run_workflow(verbose=True)


class EmittingStream:
    def __init__(self, signal):
        self._signal = signal

    def write(self, message):
        # emits the signal with the message to update the QTextEdit
        # QMetaObject.invokeMethod(self._signal, "emit", Q_ARG(str, message.strip()))
        self._signal.emit(message.strip())

    def flush(self):
        pass


class SubmitPopup(QDialog):
    def __init__(self):
        """Creates a read-only popup containing the verbose run through Workflow"""
        super(SubmitPopup, self).__init__()
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
