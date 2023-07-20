from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QListWidget,
)


class ImportForm(QWidget):
    def __init__(self):
        super().__init__()

        import_label = QLabel("Imports:")
        self.import_input = QLineEdit()
        add_button = QPushButton("Add")
        self.import_list = QListWidget()

        middle = QHBoxLayout()
        middle.addWidget(self.import_input)
        middle.addWidget(add_button)

        bottom = QVBoxLayout()
        bottom.addWidget(self.import_list)

        add_button.clicked.connect(self.add_import)
        self.imports = []

        layout = QVBoxLayout()
        layout.addWidget(import_label)

        layout.addLayout(middle)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def add_import(self):
        import_text = self.import_input.text()
        if import_text:
            self.imports.append(import_text)
            self.import_list.addItem(import_text)
            self.import_input.clear()

    def read_import(self, imports):
        if isinstance(imports, list) and all(isinstance(item, str) for item in imports):
            for i in imports:
                self.imports.append(i)
                self.import_list.addItem(i)
        self.update()

    def get_imports(self):
        return self.imports
