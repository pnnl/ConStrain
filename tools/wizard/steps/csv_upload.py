from PyQt6 import QtWidgets
import pandas as pd

from tools.wizard.steps import WizardPageIds
class CSVUploadPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.uploaded_file_path = None
        self.initUI()

    def initUI(self):
        self.setTitle("Upload a .CSV File")

        layout = QtWidgets.QVBoxLayout()

        self.uploadButton = QtWidgets.QPushButton("Upload CSV")
        self.uploadButton.clicked.connect(self.uploadCSV)

        self.filePathLabel = QtWidgets.QLabel("No file uploaded.")

        layout.addWidget(self.uploadButton)
        layout.addWidget(self.filePathLabel)
        
        self.setLayout(layout)

    def uploadCSV(self):
        options = QtWidgets.QFileDialog.Option.ReadOnly
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.uploaded_file_path = fileName
            self.filePathLabel.setText(f"Uploaded: {fileName}")

            try:
                self.wizard().data = pd.read_csv(self.uploaded_file_path)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to read CSV: {str(e)}")
                return
            self.completeChanged.emit()
        
    def isComplete(self):
        return self.uploaded_file_path is not None
    
    def nextId(self):
        return WizardPageIds.VARIABLE_MAPPING.value