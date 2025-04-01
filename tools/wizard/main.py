import sys
from PyQt6 import QtWidgets
from tools.wizard.steps.verification_case_selection import VerificationCaseSelectionPage
from tools.wizard.steps.csv_upload import CSVUploadPage
from tools.wizard.steps.variable_mapping import VariableMappingPage
from tools.wizard.steps.run_verification import RunVerificationPage
from tools.wizard.steps.path_selection import PathSelectionPage
from tools.wizard.steps import WizardPageIds

class Wizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super().__init__()

        self.setPage(WizardPageIds.PATH_SELECTION.value, PathSelectionPage())
        self.setPage(WizardPageIds.VERIFICATION_CASE_SELECTION.value, VerificationCaseSelectionPage())
        self.setPage(WizardPageIds.CSV_UPLOAD.value, CSVUploadPage())
        self.setPage(WizardPageIds.VARIABLE_MAPPING.value, VariableMappingPage())
        self.setPage(WizardPageIds.RUN_VERIFICATION.value, RunVerificationPage())

        self.setStartId(WizardPageIds.PATH_SELECTION.value)

        self.setWindowTitle("Verification Case Wizard")
        self.resize(500, 400)

    def accept(self):
        print("Wizard completed!")
        super().accept()
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    wizard = Wizard()

    wizard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()