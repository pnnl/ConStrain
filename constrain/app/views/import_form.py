from PyQt6 import QtWidgets, QtGui, QtCore

from constrain.app.utils import utils


class ImportForm(QtWidgets.QWidget):
    def __init__(self) -> None:
        """Creates an import form to be displayed when 'Import' is selected from the LHS column frame
        on the Main Window. This form allows the user to create a list of python imports to use in their
        workflow"""
        super().__init__()

        import_label = QtWidgets.QLabel("Imports:")
        self.import_input = QtWidgets.QLineEdit()

        add_button = QtWidgets.QPushButton("Add")
        add_button.setToolTip("Add a library to use in your workflow")

        self.import_list = QtWidgets.QListWidget()

        self.import_list.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.import_list.customContextMenuRequested.connect(self.show_context_menu)

        middle = QtWidgets.QHBoxLayout()
        middle.addWidget(self.import_input)
        middle.addWidget(add_button)

        bottom = QtWidgets.QVBoxLayout()
        bottom.addWidget(self.import_list)

        add_button.clicked.connect(self.add_import)

        # list of imports to be kept equal to what is in the QListWidget
        self.imports = []

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(import_label)

        layout.addLayout(middle)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def add_import(self) -> None:
        """On click of 'Add', will gather the current input and add to the display"""
        import_text = self.import_input.text()
        if import_text:
            self.imports.append(import_text)
            self.import_list.addItem(import_text)
            self.import_input.clear()

    def read_import(self, imports: list) -> None:
        """Reads a list of imports, adding each import to the display

        Args:
            imports (list): A slist of python imports
        """
        try:
            self.verify_import(imports)
        except AssertionError:
            utils.send_error("Error in Import", "Invalid imports form")
            return

        for i in imports:
            self.imports.append(i)
            self.import_list.addItem(i)
        self.update()

    def verify_import(self, imports: list) -> None:
        assert isinstance(imports, list) and all(
            isinstance(item, str) for item in imports
        )

    def show_context_menu(self, position: QtCore.QPoint) -> None:
        """Allows user to delete an import on right click of an item on the list
        Args:
            position (PyQt6.QtCore.QPoint): The position of the point where the user clicks
        """

        # find item in import list at position clicked
        item = self.import_list.itemAt(position)
        if item is None:
            return

        menu = QtWidgets.QMenu(self)
        delete_action = QtGui.QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.import_list.mapToGlobal(position))

    def delete_input(self, item: QtWidgets.QListWidgetItem) -> None:
        """Deletes a given item from the import list

        Args:
            item (PyQt6.QtWidgets.QListWidgetItem): the item to be deleted
        """
        self.imports.pop(self.import_list.row(item))
        self.import_list.takeItem(self.import_list.row(item))

    def get_imports(self) -> list:
        """Returns current imports

        Returns:
            list: a list of the current imports
        """
        return self.imports

    def contains_data(self) -> bool:
        """Check if import form contains any data"""
        return bool(self.imports)

    def clear(self) -> None:
        """Clear import form"""
        self.import_list.clear()
        self.imports.clear()
        self.import_input.clear()
        self.update()
