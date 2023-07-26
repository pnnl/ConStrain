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
import re
import json

with open("dependencies.json") as f:
    schema = json.load(f)

with open("api_to_method.json") as f:
    api_to_method = json.load(f)


class ListPopup(QDialog):
    def __init__(self, input=None, payload=True):
        super().__init__()

        self.payload = payload
        self.current_input = input if input else {} if payload else []

        self.set_ui()
        self.populate_input_list()

    def set_ui(self):
        layout = QVBoxLayout()

        self.setWindowTitle("Payloads" if self.payload else "Parameters")

        if self.payload:
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

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def populate_input_list(self):
        self.input_list.clear()

        if self.payload:
            for input in self.current_input.keys():
                self.input_list.addItem(f"{input}: {self.current_input[input]}")
        else:
            for input in self.current_input:
                self.input_list.addItem(input)

    def add_input(self):
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
        item = self.input_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.input_list.mapToGlobal(position))

    def delete_input(self, item):
        if ":" in item.text():
            self.current_input.pop(item.text().split(": ")[0])
        else:
            self.current_input.remove(item.text())

        self.populate_input_list()
        self.input_list.takeItem(self.input_list.row(item))

    def get_input(self):
        return self.current_input


class ChoicesPopup(QDialog):
    def __init__(self, payloads=[], choices=[]):
        super().__init__()

        self.payloads = payloads
        self.current_input = choices

        self.set_ui()

        self.populate_input_list()

    def set_ui(self):
        self.setWindowTitle("Choices")

        self.layout = QVBoxLayout()

        object_type_label = QLabel("Object Type")
        self.object_type_combo_box = QComboBox()
        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")
        self.object_type_combo_box.addItems(object_types)

        self.method_label = QLabel("Method")
        self.method_input = QLineEdit()
        self.method_label.hide()
        self.method_input.hide()

        self.method_combo_box = QComboBox()
        self.method_combo_box.addItems(schema[object_types[1]])
        self.method_combo_box.hide()

        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)

        self.payload_combo_box = QComboBox()
        payloads_formatted = [""]
        if self.payloads:
            payloads_formatted += [f"{item}" for item in self.payloads]
        self.payload_combo_box.addItems(payloads_formatted)

        self.object_label = QLabel("Object")
        self.object_input = self.payload_combo_box

        equals_label = QLabel("Equals")
        self.equals_input = QComboBox()
        self.equals_input.addItems(["True", "False"])

        next_label = QLabel("Next")
        self.next_input = QLineEdit()

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

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
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

    def get_object_method_from_call(self, call):
        object_pattern = r"Payloads\['(.*?)'\]"
        method_pattern = r"Payloads\['\w+'\]\.(\w+)"

        object_match = re.search(object_pattern, call)
        object = object_match.group(1) if object_match else None

        method_match = re.search(method_pattern, call)
        method = method_match.group(1) if method_match else None

        return object, method

    def populate_input_list(self):
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
        object = self.object_input.currentText()
        method = (
            self.method_input.text()
            if object == "Custom"
            else self.method_combo_box.currentText()
        )
        equals = self.equals_input.currentText()
        next = self.next_input.text()

        print(object, method, equals, next)
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
        item = self.input_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.input_list.mapToGlobal(position))

    def delete_input(self, item):
        self.current_input.pop(self.input_list.row(item))
        self.populate_input_list()
        self.input_list.takeItem(self.input_list.row(item))

    def get_input(self):
        return self.current_input
