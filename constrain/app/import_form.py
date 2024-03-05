from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QMenu,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class ImportForm(QWidget):
    def __init__(self):
        """Creates an import form to be displayed when 'Import' is selected from the LHS column frame
        on the Main Window. This form allows the user to create a list of python imports to use in their
        workflow"""
        super().__init__()

        import_label = QLabel("Imports:")
        self.import_input = QLineEdit()

        add_button = QPushButton("Add")

        self.import_list = QListWidget()

        self.import_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.import_list.customContextMenuRequested.connect(self.show_context_menu)

        middle = QHBoxLayout()
        middle.addWidget(self.import_input)
        middle.addWidget(add_button)

        bottom = QVBoxLayout()
        bottom.addWidget(self.import_list)

        add_button.clicked.connect(self.add_import)

        # list of imports to be kept equal to what is in the QListWidget
        self.imports = []

        layout = QVBoxLayout()
        layout.addWidget(import_label)

        layout.addLayout(middle)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def add_import(self):
        """On click of 'Add', will gather the current input and add to the display"""
        import_text = self.import_input.text()
        if import_text:
            self.imports.append(import_text)
            self.import_list.addItem(import_text)
            self.import_input.clear()

    def read_import(self, imports):
        """Reads a list of imports, adding each import to the display

        Args:
            imports (list): A list of python imports
        """
        if isinstance(imports, list) and all(isinstance(item, str) for item in imports):
            for i in imports:
                self.imports.append(i)
                self.import_list.addItem(i)
        self.update()

    def show_context_menu(self, position):
        """Allows user to delete an import on right click of an item on the list
        Args:
            position (PyQt6.QtCore.QPoint): The position of the point where the user clicks
        """

        # find item in import list at position clicked
        item = self.import_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.import_list.mapToGlobal(position))

    def delete_input(self, item):
        """Deletes a given item from the import list

        Args:
            item (PyQt6.QtWidgets.QListWidgetItem): the item to be deleted
        """
        self.imports.pop(self.import_list.row(item))
        self.import_list.takeItem(self.import_list.row(item))

    def get_imports(self):
        """Returns current imports

        Returns:
            list: a list of the current imports
        """
        return self.imports

    def contains_data(self):
        """Check if import form contains any data"""
        return bool(self.imports)

    def clear(self):
        """Clear import form"""
        self.import_list.clear()
        self.imports.clear()
        self.import_input.clear()
        self.update()
