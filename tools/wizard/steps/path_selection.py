from PyQt6 import QtWidgets
from tools.wizard.steps import WizardPageIds


class PathSelectionPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Select a Path")

        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Choose a path:")
        layout.addWidget(label)

        self.singleVerificationItem = QtWidgets.QRadioButton("Single Verification Item")
        self.multipleVerificationItems = QtWidgets.QRadioButton(
            "Multiple Verification Items"
        )
        self.constrainAnalysis = QtWidgets.QRadioButton("ConStrain Analysis")
        self.newVerificationItem = QtWidgets.QRadioButton("New Verification Item")

        layout.addWidget(self.singleVerificationItem)
        layout.addWidget(self.multipleVerificationItems)
        layout.addWidget(self.constrainAnalysis)
        layout.addWidget(self.newVerificationItem)

        self.singleVerificationItem.setChecked(True)

        self.setLayout(layout)

    def initializePage(self):
        self.multipleVerificationItems.setEnabled(False)
        self.constrainAnalysis.setEnabled(False)
        self.newVerificationItem.setEnabled(False)

    def nextId(self):
        if self.singleVerificationItem.isChecked():
            return WizardPageIds.VERIFICATION_CASE_SELECTION.value
        elif self.multipleVerificationItems.isChecked():
            return WizardPageIds.MULTIPLE_ITEMS.value
        elif self.constrainAnalysis.isChecked():
            return WizardPageIds.CONSTRAIN_ANALYSIS.value
        elif self.newVerificationItem.isChecked():
            return WizardPageIds.NEW_ITEM.value
        return -1
