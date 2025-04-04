import json

import pandas as pd
from PyQt6 import QtWidgets

from tools.wizard.utils.load_schemas import load_verification_cases_library
from tools.wizard.steps import WizardPageIds


class VariableMappingPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.datapoint_mapping = {"dev_settings": {}, "parameters": {}}
        self.verification_case_library = load_verification_cases_library()
        self.datapoints_keys = None

        self.previous_uploaded_data, self.current_uploaded_data = None, None
        self.previous_verification_class, self.current_verification_class = None, None

        self.initUI()

    def initUI(self):
        self.setTitle("Compare CSV Columns with Description Datapoints")

        layout = QtWidgets.QVBoxLayout()

        self.mappingLayout = QtWidgets.QFormLayout()
        self.mappingWidgets = {}

        layout.addLayout(self.mappingLayout)

        self.setLayout(layout)

    def initializePage(self):
        self.set_current_verification_class_and_upload_path()

        if (
            self.current_uploaded_data is None
            or (
                all(
                    isinstance(i, pd.DataFrame)
                    for i in [self.current_uploaded_data, self.previous_uploaded_data]
                )
                and not self.current_uploaded_data.equals(self.previous_uploaded_data)
            )
            or self.current_verification_class != self.previous_verification_class
        ):
            self.reset_mappings()
        else:
            return

        csv_columns = list(self.current_uploaded_data)

        csv_columns.insert(0, "Use Parameter")

        # Get the selected verification case
        case_details = self.verification_case_library[self.current_verification_class]
        self.datapoints_keys = case_details["description_datapoints"].keys()

        headerLayout = QtWidgets.QHBoxLayout()
        self.mappingLayout.addRow(headerLayout)

        for key in self.datapoints_keys:
            hBoxLayout = QtWidgets.QHBoxLayout()

            # Create and add QComboBox
            comboBox = QtWidgets.QComboBox()
            comboBox.addItems(csv_columns)
            if key in self.datapoint_mapping:
                comboBox.setCurrentText(self.datapoint_mapping[key])
            elif key in csv_columns:
                comboBox.setCurrentText(key)
            else:
                comboBox.setCurrentIndex(0)  # Default to "Use Parameter"
            hBoxLayout.addWidget(comboBox)

            # Create and add QLineEdit
            lineEdit = QtWidgets.QLineEdit()
            lineEdit.setVisible(comboBox.currentText() == "Use Parameter")
            if key in self.datapoint_mapping:
                lineEdit.setText(self.datapoint_mapping[key])
            hBoxLayout.addWidget(lineEdit)

            # Connect comboBox signal to slot for changing QLineEdit visibility
            comboBox.currentTextChanged.connect(
                lambda text, le=lineEdit: le.setVisible(text == "Use Parameter")
            )

            # Add the hBoxLayout with both options to the mapping layout
            self.mappingLayout.addRow(QtWidgets.QLabel(key), hBoxLayout)
            self.mappingWidgets[key] = (comboBox, lineEdit)  # Store both widgets

    def cleanupPage(self):
        super().cleanupPage()
        self.set_datapoint_mapping()

    def set_current_verification_class_and_upload_path(self):
        self.previous_uploaded_data = self.current_uploaded_data
        csv_upload_page = self.wizard().page(WizardPageIds.CSV_UPLOAD.value)
        self.current_uploaded_data = csv_upload_page.data

        self.previous_verification_class = self.current_verification_class
        self.current_verification_class = self.wizard().selected_verification_class

    def set_datapoint_mapping(self):
        self.datapoint_mapping = {"parameters": {}, "dev_settings": {}}

        for key in self.datapoints_keys:
            comboBox, lineEdit = self.mappingWidgets[key]

            # Prioritize the QLineEdit if it has text
            if lineEdit.text():
                self.datapoint_mapping["parameters"][key] = float(lineEdit.text())
            else:
                self.datapoint_mapping["dev_settings"][key] = comboBox.currentText()

        self.wizard().datapoint_mapping = self.datapoint_mapping

    def reset_mappings(self):
        self.datapoint_mapping = {"dev_settings": {}, "parameters": {}}
        self.wizard().datapoint_mapping = self.datapoint_mapping
        self.clear_layout(self.mappingLayout)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
                item.layout().deleteLater()

    def isComplete(self):
        self.set_datapoint_mapping()
        return True

    def nextId(self):
        return WizardPageIds.RUN_VERIFICATION.value

    def restart(self):
        self.reset_mappings()
        self.previous_uploaded_data, self.current_uploaded_data = None, None
        self.previous_verification_class, self.current_verification_class = None, None
