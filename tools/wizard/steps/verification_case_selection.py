import json

from PyQt6 import QtWidgets

from tools.wizard.utils.load_schemas import load_verification_cases_library
from tools.wizard.steps import WizardPageIds


class VerificationCaseSelectionPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_verification_class = None
        self._verification_cases_library = load_verification_cases_library()

        self.initUI()

    def initUI(self):
        self.setTitle("Select an Item")

        layout = QtWidgets.QVBoxLayout()

        self.searchBox = QtWidgets.QLineEdit()
        self.searchBox.setPlaceholderText("Search")
        self.searchBox.textChanged.connect(self.filterTree)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Available Items"])
        for key in self._verification_cases_library.keys():
            item = QtWidgets.QTreeWidgetItem([key])
            self.tree.addTopLevelItem(item)

        self.tree.currentItemChanged.connect(self.onItemSelected)

        self.selectionLabel = QtWidgets.QLabel("Please select an item from the list.")

        layout.addWidget(self.searchBox)
        layout.addWidget(self.tree)
        layout.addWidget(self.selectionLabel)

        self.setLayout(layout)

    def filterTree(self):
        filter_text = self.searchBox.text().lower()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setHidden(filter_text not in item.text(0).lower())

    def onItemSelected(self, current, previous):
        if current:
            selected_item = current.text(0)
            self.selectionLabel.setText(f"Selected Item: {selected_item}")

            self.selected_verification_class = selected_item
            self.wizard().selected_verification_class = self.selected_verification_class

            self.completeChanged.emit()

            if current != previous:
                variable_mapping_page = self.wizard().page(
                    WizardPageIds.VARIABLE_MAPPING.value
                )
                variable_mapping_page.reset_mappings()

    def restart(self):
        self.searchBox.clear()
        self.selected_verification_class = None
        self.wizard().selected_verification_class = None
        self.selectionLabel.clear()

    def isComplete(self):
        return self.selected_verification_class is not None

    def nextId(self):
        return WizardPageIds.CSV_UPLOAD.value
