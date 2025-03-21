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
from constrain.app import utils


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
        try:
            self.verify_import(workflow_name=workflow_name, meta=meta)
        except AssertionError:
            utils.send_error("Error in Import", "Invalid meta form")
            return

        self.name_input.setText(workflow_name)
        self.author_input.setText(meta.get("author"))
        d = QDate.fromString(meta.get("date"), self.date_format)
        self.date_input.setDate(d)
        self.version_input.setText(meta.get("version"))
        self.description_input.setText(meta.get("description"))

        self.update()

    def verify_import(self, workflow_name=None, meta=None):
        def is_str(input):
            return isinstance(input, str)

        if workflow_name:
            assert is_str(workflow_name)

        if isinstance(meta, dict):
            for k in ["author", "date", "version", "description"]:
                if v := meta.get(k):
                    assert is_str(v)

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
