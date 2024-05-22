import sys
import warnings

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
