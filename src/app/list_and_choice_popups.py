from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QListWidget,
    QDialog,
    QDialogButtonBox,
    QMenu,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

import os
import re
import json

# mapping from object to its methods and its methods to its parameters for display in popup

script_directory = os.path.dirname(os.path.abspath(__file__))
dependencies_path = os.path.join(script_directory, "dependencies.json")
api_to_method_path = os.path.join(script_directory, "api_to_method.json")

with open(dependencies_path) as f:
    schema = json.load(f)

# mapping from object to its methods using the true method names
with open(api_to_method_path) as f:
    api_to_method = json.load(f)


class ListPopup(QDialog):
    def __init__(self, input=None, payload=True):
        """Popup that will display for either parameters (Custom object) or payloads (all other objects) when
        selected in the basic popup. Currently remade each time it is chosen instead of being saved inside of
        the BasicPopup or CustomItem

        Args:
            input (dict or list): a data structure containing what should be in the list widget
            payload (bool): whether or not the ListPopup is being used for payloads
        """
        super().__init__()

        self.payload = payload
        self.current_input = input if input else {} if payload else []

        self.set_ui()
        self.populate_input_list()

    def set_ui(self):
        """Creates the layout of the ListPopup. Will make different layout depending on whether ListPopup
        is for payloads or parameters
        """
        layout = QVBoxLayout()

        self.setWindowTitle("Payloads" if self.payload else "Parameters")

        layout.addWidget(QLabel("Name:"))
        self.name_line_edit = QLineEdit()
        layout.addWidget(self.name_line_edit)

        layout.addWidget(QLabel("Payload:" if self.payload else "Parameter:"))
        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_input)
        layout.addWidget(add_button)

        self.input_list = QListWidget()
        self.input_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.input_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.input_list)

        # accept or cancel changes
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def populate_input_list(self):
        """Populates the input list depending on what is in the current input. The input
        list contains a formatted string version of the inputs.
        """
        # TODO: Figure out why I decided to reset input_list instead of just appending
        self.input_list.clear()

        if self.payload:
            # use payload formatting
            for input in self.current_input.keys():
                # only add if input exists
                if input != "":
                    self.input_list.addItem(f"{input}: {self.current_input[input]}")
        else:
            for input in self.current_input:
                # only add if input exists
                if input != "":
                    self.input_list.addItem(input)

    def add_input(self):
        """Adds input to input list on the click of 'Add' button"""

        # retrieve current text
        title = self.name_line_edit.text()
        input = self.line_edit.text()

        if self.payload:
            self.current_input[title] = input
        else:
            self.current_input.append(input)

        self.populate_input_list()
        self.name_line_edit.clear()
        self.line_edit.clear()

    def show_context_menu(self, position):
        """Allows user to delete an import on right click of an item on the list
        Args:
            position (PyQt6.QtCore.QPoint): The position of the point where the user clicks
        """
        item = self.input_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.input_list.mapToGlobal(position))

    def delete_input(self, item):
        """Deletes a given item from the import list

        Args:
            item (PyQt6.QtWidgets.QListWidgetItem): the item to be deleted
        """
        if ":" in item.text():
            self.current_input.pop(item.text().split(": ")[0])
        else:
            self.current_input.remove(item.text())

        self.input_list.takeItem(self.input_list.row(item))

    def get_input(self):
        """Returns:
        (list or dict): the parameters or payloads in this form
        """
        return self.current_input


class ChoicesPopup(QDialog):
    def __init__(self, payloads=[], choices=[]):
        """Popup displayed for creating choices in the basic popup. Currently remade each time it is
        chosen instead of being stored inside of a BasicPopup or CustomItem

        Args:
            payloads (list): The list of objects that are available to be chosen from
            choices (list): A list of previously created choices in strings to be displayed in
            the list widget
        """
        super().__init__()

        self.payloads = payloads
        self.current_input = choices

        self.set_ui()

        self.populate_input_list()

    def set_ui(self):
        """Sets the layout for the popup"""
        self.setWindowTitle("Choices")

        self.layout = QVBoxLayout()

        # form
        object_type_label = QLabel("Object Type")
        self.object_type_combo_box = QComboBox()
        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")
        self.object_type_combo_box.addItems(object_types)

        # hide until object type is chosen
        self.method_label = QLabel("Method")
        self.method_label.hide()

        # Line for method if Custom object, hide until Custom is chosen
        self.method_input = QLineEdit()
        self.method_input.hide()

        # hide this until non-Custom object is chosen
        self.method_combo_box = QComboBox()
        self.method_combo_box.hide()

        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)

        # possible objects to choose from
        self.payload_combo_box = QComboBox()
        payloads_formatted = [""]
        if self.payloads:
            payloads_formatted += [f"{item}" for item in self.payloads]
        self.payload_combo_box.addItems(payloads_formatted)

        self.object_label = QLabel("Object")
        self.object_input = self.payload_combo_box

        # equals
        equals_label = QLabel("Equals")
        self.equals_input = QComboBox()
        self.equals_input.addItems(["True", "False"])

        # next
        next_label = QLabel("Next")
        self.next_input = QLineEdit()

        # add
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_input)

        # buttons for accept or reject
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # displayed list to store input in strings
        self.input_list = QListWidget()
        self.input_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.input_list.customContextMenuRequested.connect(self.show_context_menu)

        self.layout.addWidget(object_type_label)
        self.layout.addWidget(self.object_type_combo_box)
        self.layout.addWidget(self.method_label)
        self.layout.addWidget(self.method_input)
        self.layout.addWidget(self.method_combo_box)
        self.layout.addWidget(self.object_label)
        self.layout.addWidget(self.object_input)
        self.layout.addWidget(equals_label)
        self.layout.addWidget(self.equals_input)
        self.layout.addWidget(next_label)
        self.layout.addWidget(self.next_input)
        self.layout.addWidget(add_button)
        self.layout.addWidget(self.input_list)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    def on_state_selected(self):
        """Sets UI based on which object type is selected"""
        object_type = self.object_type_combo_box.currentText()
        self.method_combo_box.clear()

        if object_type == "Custom":
            self.method_combo_box.hide()
            self.object_label.hide()
            self.object_input.hide()
            self.method_label.show()
            self.method_input.show()

        else:
            self.method_input.hide()
            self.method_label.show()
            methods = schema[object_type].keys()
            self.method_combo_box.addItems(methods)
            self.method_combo_box.show()

    def clear_form(self):
        """Deletes entire form"""
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

    def get_object_method_from_call(self, call):
        """Searches method call to retrieve object and method used on the object

        Args:
            call (str): a method call

        Returns:
            str: The object, None if not found
            str: The method, None if not found
        """
        object_pattern = r"Payloads\['(.*?)'\]"
        method_pattern = r"Payloads\['\w+'\]\.(\w+)"

        object_match = re.search(object_pattern, call)
        object = object_match.group(1) if object_match else None

        method_match = re.search(method_pattern, call)
        method = method_match.group(1) if method_match else None

        return object, method

    def populate_input_list(self):
        """Fills input list widget with formatted strings based on the choice/s defined"""
        self.input_list.clear()

        if self.current_input:
            for choice in self.current_input:
                object, method = self.get_object_method_from_call(choice["Value"])
                if not object or not method:
                    method = choice["Value"]
                    widget_line = f"{method} = {choice['Equals']} -> {choice['Next']}"
                else:
                    widget_line = f"Payloads['{object}'].{method} = {choice['Equals']} -> {choice['Next']}"
                self.input_list.addItem(widget_line)

    def add_input(self):
        """On choice addition, adds choice dict to current list and repopulates list widget"""
        object = self.object_input.currentText()
        method = (
            self.method_input.text()
            if object == "Custom"
            else self.method_combo_box.currentText()
        )
        equals = self.equals_input.currentText()
        next = self.next_input.text()

        if method and equals and next:
            if object != "":
                value = f"Payloads['{object}'].{method}"
            else:
                value = method

            self.current_input.append({"Value": value, "Equals": equals, "Next": next})
            self.populate_input_list()
            self.equals_input.clear()
            self.next_input.clear()

    def show_context_menu(self, position):
        """Allows user to delete an import on right click of an item on the list
        Args:
            position (PyQt6.QtCore.QPoint): The position of the point where the user clicks
        """
        item = self.input_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.input_list.mapToGlobal(position))

    def delete_input(self, item):
        """Deletes a given item from the import list

        Args:
            item (PyQt6.QtWidgets.QListWidgetItem): the item to be deleted
        """
        self.current_input.pop(self.input_list.row(item))
        self.input_list.takeItem(self.input_list.row(item))

    def get_input(self):
        """Returns list of choice dicts

        Returns:
            list: list containing all choice dicts that currently exist in the popup
        """
        return self.current_input
