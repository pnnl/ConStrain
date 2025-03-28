from PyQt6 import QtWidgets
import pandas
import json
import tempfile
from constrain.api.verification_case import VerificationCase
from constrain.api.verification import Verification
from tools.wizard.utils.load_schemas import LIBRARY_PATH

class RunVerificationPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verification_cases = {"cases": []}
        self.initUI()

    def initUI(self):
        self.setTitle("Run Verification")

        layout = QtWidgets.QVBoxLayout()

        self.uploadButton = QtWidgets.QPushButton("Run Verification")
        self.uploadButton.clicked.connect(self.runVerification)

        layout.addWidget(self.uploadButton)
        
        self.setLayout(layout)

    def runVerification(self):
        verification_class = self.wizard().selected_verification_class

        mapping_page = self.wizard().page(2)
        mapping_page.set_datapoint_mapping()
        mapping = self.wizard().datapoint_mapping

        csv_upload_page = self.wizard().page(1)
        uploaded_file_path = csv_upload_page.uploaded_file_path

        self.verification_cases = {"cases": []}
        self.createVerificationCase(verification_class, mapping)

        tmpdir = tempfile.TemporaryDirectory()

        
        verification_case = VerificationCase(self.verification_cases['cases'])
        verification = Verification(verification_case)

        verification.configure(
            output_path=tmpdir.name,
            time_series_csv_export_name=uploaded_file_path,
            lib_items_path=LIBRARY_PATH,
            plot_option=None,
            fig_size=(6, 5),
            num_threads=2,
        )

        verification.run()


    def createVerificationCase(self, verification_class, mapping):
        cases = self.verification_cases["cases"]

        keys = ["parameters", "dev_settings"]
        for k in keys:
            if k in mapping and not mapping.get(k):
                mapping.pop(k)
            
        cases.append({
            "no": len(cases) + 1,
            "run_simulation": False,
            "expected_result": "pass",
            "datapoints_source": mapping,
            "verification_class": verification_class
        })