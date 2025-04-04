from PyQt6 import QtCore
import sys, os
from constrain.api.verification import Verification
from constrain.app.submit import EmittingStream
from constrain.api.reporting import Reporting


class VerificationCaseRunner(QtCore.QThread):
    update_text = QtCore.pyqtSignal(str)

    def __init__(self, verification: Verification):
        super(VerificationCaseRunner, self).__init__()
        self.verification = verification

    def run(self):
        sys.stdout = EmittingStream(self.update_text)
        try:
            self.verification.run()
            reporting = Reporting(
                verification_json=f"{os.getcwd()}/*_md.json",
                result_md_name="report_summary.md",
                report_format="markdown",
            )
            reporting.report_multiple_cases()
        finally:
            print("Verification Complete")
            sys.stdout = sys.__stdout__  # Reset stdout to original
