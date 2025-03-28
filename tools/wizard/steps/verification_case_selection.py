import json

from PyQt6 import QtWidgets

from tools.wizard.utils.load_schemas import load_verification_cases_library, load_verification_cases_schema

class VerificationCaseSelectionPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_verification_class = None
        self._verification_cases_library = load_verification_cases_library()
        self._verification_cases_schema = load_verification_cases_schema()

        self.initUI()

    def initUI(self):
        self.setTitle("Select an Item")
        
        layout = QtWidgets.QVBoxLayout()
        
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Available Items"])

        for key in self._verification_cases_library.keys():
            item = QtWidgets.QTreeWidgetItem([key])
            self.tree.addTopLevelItem(item)
        
        self.tree.currentItemChanged.connect(self.onItemSelected)
        
        self.selectionLabel = QtWidgets.QLabel("Please select an item from the list.")

        layout.addWidget(self.tree)
        layout.addWidget(self.selectionLabel)
        
        self.setLayout(layout)

    def onItemSelected(self, current, previous):
        if current:
            selected_item = current.text(0)
            self.selectionLabel.setText(f"Selected Item: {selected_item}")
            self.wizard().selected_verification_class = selected_item