import json

import pandas as pd
from PyQt6 import QtWidgets

from tools.wizard.utils.load_schemas import load_verification_cases_schema, load_verification_cases_library

class VariableMappingPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.datapoint_mapping = {"dev_settings": {}, "parameters": {}}
        self.verification_case_library = load_verification_cases_library()
        self.datapoints_keys = None
        self.data = None

        self.initUI()


    def initUI(self):
        self.setTitle("Compare CSV Columns with Description Datapoints")

        layout = QtWidgets.QVBoxLayout()
        
        self.mappingLayout = QtWidgets.QFormLayout()
        self.mappingWidgets = {}

        layout.addLayout(self.mappingLayout)
        
        self.setLayout(layout)

    def initializePage(self):
        # Clear previous mappings
        while self.mappingLayout.count():
            item = self.mappingLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Get the uploaded file path and selected verification case
        csv_upload_page = self.wizard().page(1)
        uploaded_file_path = csv_upload_page.uploaded_file_path

        if uploaded_file_path:
            self.data = pd.read_csv(uploaded_file_path)
            csv_columns = list(self.data.columns)

            csv_columns.insert(0, "Use Parameter")

            # Get the selected verification case
            selected_class = self.wizard().selected_verification_class
            case_details = self.verification_case_library[selected_class]
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
                comboBox.currentTextChanged.connect(lambda text, le=lineEdit: le.setVisible(text == "Use Parameter"))
                
                # Add the hBoxLayout with both options to the mapping layout
                self.mappingLayout.addRow(QtWidgets.QLabel(key), hBoxLayout)
                self.mappingWidgets[key] = (comboBox, lineEdit)  # Store both widgets

    def cleanupPage(self):
        self.set_datapoint_mapping()
        
    def isNumeric(self, key):
        selected_class = self.wizard().selected_verification_class

        if key not in self.verification_cases_schema["$defs"][selected_class]["properties"]["datapoints_source"]["properties"]["idf_output_variables"]["properties"]:
            return True
        return False
    
    def set_datapoint_mapping(self):
        self.datapoint_mapping = {"parameters": {}, "dev_settings": {}}

        for key in self.datapoints_keys:
            comboBox, lineEdit = self.mappingWidgets[key]
            
            # Prioritize the QLineEdit if it has text
            if lineEdit.text():
                self.datapoint_mapping["parameters"][key] = lineEdit.text()
            else:
                self.datapoint_mapping["dev_settings"][key] = comboBox.currentText()

        self.wizard().datapoint_mapping = self.datapoint_mapping
    
    def isComplete(self):
        self.set_datapoint_mapping()
        return True