from PyQt6 import QtCore, QtWidgets

from constrain.app.utils import utils


class MetaForm(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        name_label = QtWidgets.QLabel("Workflow Name:")
        self.name_input = QtWidgets.QLineEdit()

        author_label = QtWidgets.QLabel("Author:")
        self.author_input = QtWidgets.QLineEdit()

        date_label = QtWidgets.QLabel("Date:")
        self.date_input = QtWidgets.QDateEdit()
        self.date_format = "MM/dd/yyyy"
        self.date_input.setDisplayFormat(self.date_format)

        version_label = QtWidgets.QLabel("Version:")
        self.version_input = QtWidgets.QLineEdit()

        description_label = QtWidgets.QLabel("Description:")
        self.description_input = QtWidgets.QTextEdit()

        layout = QtWidgets.QVBoxLayout()

        top = QtWidgets.QHBoxLayout()
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

    def get_meta(self) -> dict:
        return {
            "author": self.author_input.text(),
            "date": self.date_input.text(),
            "version": self.version_input.text(),
            "description": self.description_input.toPlainText(),
        }

    def read_import(self, workflow_name: str = None, meta: str = None) -> None:
        try:
            self.verify_import(workflow_name=workflow_name, meta=meta)
        except AssertionError:
            utils.send_error("Error in Import", "Invalid meta form")
            return

        self.name_input.setText(workflow_name)
        self.author_input.setText(meta.get("author"))
        d = QtCore.QDate.fromString(meta.get("date"), self.date_format)
        self.date_input.setDate(d)
        self.version_input.setText(meta.get("version"))
        self.description_input.setText(meta.get("description"))

        self.update()

    def verify_import(self, workflow_name: str = None, meta: str = None) -> None:
        def is_str(input):
            return isinstance(input, str)

        if workflow_name:
            assert is_str(workflow_name)

        if isinstance(meta, dict):
            for k in ["author", "date", "version", "description"]:
                if v := meta.get(k):
                    assert is_str(v)

    def get_workflow_name(self) -> str:
        return self.name_input.text()

    def contains_data(self) -> bool:
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

    def clear(self) -> None:
        """Clear meta form"""
        self.name_input.clear()
        self.author_input.clear()
        self.date_input.clear()
        self.version_input.clear()
        self.description_input.clear()
        self.update()
