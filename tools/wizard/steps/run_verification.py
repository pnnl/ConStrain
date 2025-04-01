from PyQt6 import QtWidgets
import tempfile
import shutil
import atexit
from constrain.api.verification_case import VerificationCase
from constrain.api.verification import Verification
from tools.wizard.utils.load_schemas import LIBRARY_PATH
from tools.wizard.components.verification_case_runner import VerificationCaseRunner
from tools.wizard.steps import WizardPageIds


class RunVerificationPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verification_cases = {"cases": []}

        self.previous_uploaded_file_path, self.current_uploaded_file_path = None, None
        self.previous_verification_class, self.current_verification_class = None, None

        self.tmpdir = None

        self.initUI()

    def initUI(self):
        self.setTitle("Run Verification")

        layout = QtWidgets.QVBoxLayout()

        self.uploadButton = QtWidgets.QPushButton("Run Verification")
        self.uploadButton.clicked.connect(self.runVerification)
        layout.addWidget(self.uploadButton)

        self.outputTextEdit = QtWidgets.QTextEdit()
        self.outputTextEdit.setReadOnly(True)  # Make the text edit read-only
        layout.addWidget(self.outputTextEdit)

        self.setLayout(layout)

    def append_output(self, message):
        self.outputTextEdit.append(message)

    def initializePage(self):
        self.set_current_verification_class_and_upload_path()

        if (
            self.current_uploaded_file_path != self.previous_uploaded_file_path
            or self.current_verification_class != self.previous_verification_class
        ):
            self.outputTextEdit.clear()

    def runVerification(self):
        self.outputTextEdit.clear()
        self.uploadButton.setEnabled(False)
        verification_class = self.wizard().selected_verification_class

        mapping_page = self.wizard().page(WizardPageIds.VARIABLE_MAPPING.value)
        mapping_page.set_datapoint_mapping()
        mapping = self.wizard().datapoint_mapping

        csv_upload_page = self.wizard().page(WizardPageIds.CSV_UPLOAD.value)
        uploaded_file_path = csv_upload_page.uploaded_file_path

        self.verification_cases = {"cases": []}
        self.create_verification_case(verification_class, mapping)

        self.tmpdir = tempfile.TemporaryDirectory()
        verification_case = VerificationCase(self.verification_cases["cases"])
        verification = Verification(verification_case)
        verification.configure(
            output_path=self.tmpdir.name,
            time_series_csv_export_name=uploaded_file_path,
            lib_items_path=LIBRARY_PATH,
            plot_option=None,
            fig_size=(6, 5),
            num_threads=2,
        )

        self.verification_runner = VerificationCaseRunner(verification)
        self.verification_runner.update_text.connect(self.append_output)
        self.verification_runner.finished.connect(self.cleanup_tmpdir)
        self.verification_runner.finished.connect(
            lambda: self.uploadButton.setEnabled(True)
        )
        self.verification_runner.start()

    def cleanup_tmpdir(self):
        if self.tmpdir:
            shutil.rmtree(self.tmpdir.name)

    def create_verification_case(self, verification_class, mapping):
        cases = self.verification_cases["cases"]

        keys = ["parameters", "dev_settings"]
        for k in keys:
            if k in mapping and not mapping.get(k):
                mapping.pop(k)

        csv_upload_page = self.wizard().page(WizardPageIds.CSV_UPLOAD.value)
        uploaded_file_path = csv_upload_page.uploaded_file_path
        cases.append(
            {
                "no": len(cases) + 1,
                "run_simulation": False,
                "expected_result": "pass",
                "simulation_IO": {
                    "output": uploaded_file_path,
                },
                "datapoints_source": mapping,
                "verification_class": verification_class,
            }
        )

    def set_current_verification_class_and_upload_path(self):
        self.previous_uploaded_file_path = self.current_uploaded_file_path
        csv_upload_page = self.wizard().page(WizardPageIds.CSV_UPLOAD.value)
        self.current_uploaded_file_path = csv_upload_page.uploaded_file_path

        self.previous_verification_class = self.current_verification_class
        self.current_verification_class = self.wizard().selected_verification_class

    def nextId(self):
        return -1
