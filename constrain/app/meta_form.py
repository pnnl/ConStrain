from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtCore import QDate


class MetaForm(QWidget):
    def __init__(self):
        super().__init__()

        name_label = QLabel("Workflow Name:")
        self.name_input = QLineEdit()

        author_label = QLabel("Author:")
        self.author_input = QLineEdit()

        date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_format = "MM/dd/yyyy"
        self.date_input.setDisplayFormat(self.date_format)

        version_label = QLabel("Version:")
        self.version_input = QLineEdit()

        description_label = QLabel("Description:")
        self.description_input = QTextEdit()

        layout = QVBoxLayout()

        top = QHBoxLayout()
        top.addWidget(name_label)
        top.addWidget(self.name_input)
        top.addWidget(author_label)
        top.addWidget(self.author_input)
        top.addWidget(date_label)
        top.addWidget(self.date_input)
        top.addWidget(version_label)
        top.addWidget(self.version_input)

        layout.addLayout(top)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)

        self.setLayout(layout)

    def get_meta(self):
        return {
            "author": self.author_input.text(),
            "date": self.date_input.text(),
            "version": self.version_input.text(),
            "description": self.description_input.toPlainText(),
        }

    def read_import(self, workflow_name=None, meta=None):
        def isStr(input):
            return isinstance(input, str)

        if workflow_name:
            if isStr(workflow_name):
                self.name_input.setText(workflow_name)
            else:
                print("error")

        if isinstance(meta, dict):
            if "author" in meta.keys():
                author = meta["author"]
                if isStr(author):
                    self.author_input.setText(author)
                else:
                    print("invalid author")
            if "date" in meta.keys():
                date = meta["date"]
                if isStr(date):
                    d = QDate.fromString(date, self.date_format)
                    self.date_input.setDate(d)
                else:
                    print("invalid date")
            if "version" in meta.keys():
                version = meta["version"]
                if isStr(version):
                    self.version_input.setText(version)
                else:
                    print("invalid version")
            if "description" in meta.keys():
                description = meta["description"]
                if isStr(description):
                    self.description_input.setText(description)
                else:
                    print("invalid description")
        self.update()

    def get_workflow_name(self):
        return self.name_input.text()

    def contains_data(self):
        """Check if meta form contains any data"""
        return all(
            [
                self.name_input.text(),
                self.author_input.text(),
                self.date_input.text(),
                self.version_input.text(),
                self.description_input.toPlainText(),
            ]
        )

    def clear(self):
        """Clear meta form"""
        self.name_input.clear()
        self.author_input.clear()
        self.date_input.clear()
        self.version_input.clear()
        self.description_input.clear()
        self.update()
