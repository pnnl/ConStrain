from PyQt6 import QtCore
import sys
from constrain.api.verification import Verification
from constrain.app.submit import EmittingStream


class VerificationCaseRunner(QtCore.QThread):
    update_text = QtCore.pyqtSignal(str)
    
    def __init__(self, verification: Verification):
        super(VerificationCaseRunner, self).__init__()
        self.verification = verification

    def run(self):
        sys.stdout = EmittingStream(self.update_text)
        try:
            self.verification.run()
        finally:
            sys.stdout = sys.__stdout__  # Reset stdout to original
            