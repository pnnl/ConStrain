from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QListWidget,
    QDialog,
    QGroupBox,
    QDialogButtonBox,
    QMenu,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import json
import re

with open("dependencies.json") as f:
    schema = json.load(f)

with open("api_to_method.json") as f:
    api_to_method = json.load(f)


class PopupWindow(QDialog):
    def __init__(self, payloads={}, edit=False, state=None):
        super().__init__()
        self.current_payloads = None
        self.current_params = None
        self.current_choices = None
        self.error = False
        # self.payload_to_payload_type = {}

        self.type_combo_box = QComboBox()
        self.object_type_combo_box = QComboBox()
        self.method_combo_box = QComboBox()
        self.form_layout = QVBoxLayout()

        self.buttons = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.setFixedSize(100, 20)
        self.save_button.clicked.connect(self.save)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(100, 20)
        self.cancel_button.clicked.connect(self.close)

        self.payload_button = QPushButton("Edit")
        self.payload_button.setFixedSize(100, 20)
        self.payload_button.clicked.connect(self.payload_form)

        self.payload_list_widget = QListWidget()
        self.parameter_list_widget = QListWidget()

        self.buttons.addWidget(self.save_button)
        self.buttons.addWidget(self.cancel_button)

        self.payloads = payloads
        self.form_data = {}

        self.initialize_ui()

    def initialize_ui(self):
        self.setWindowTitle("Add State")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.type_combo_box.addItems(["", "MethodCall", "Choice"])

        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")

        self.object_type_combo_box.addItems(object_types)
        self.method_combo_box.addItems(schema[object_types[1]])

        layout.addWidget(self.type_combo_box)
        layout.addWidget(self.object_type_combo_box)
        layout.addWidget(self.method_combo_box)

        self.object_type_combo_box.hide()
        self.method_combo_box.hide()

        layout.addLayout(self.form_layout)
        layout.addLayout(self.buttons)

        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)
        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)
        self.method_combo_box.currentIndexChanged.connect(
            lambda: self.update_form(False)
        )

    def edit_mode(self, payloads, rect):
        self.setWindowTitle("Edit State")
        self.payloads = payloads
        if self.payloads and self.payload_combo_box:
            payload_objects_created_in_popup = rect.get_objects_created()
            current = self.payload_combo_box.currentText()
            self.payload_combo_box.clear()
            payloads_formatted = [
                f"{item}"
                for item in self.payloads
                if item not in payload_objects_created_in_popup
            ]
            payloads_formatted.insert(0, "")
            self.payload_combo_box.addItems(payloads_formatted)
            self.payload_combo_box.setCurrentText(current)

    def on_type_selected(self):
        type = self.type_combo_box.currentText()
        self.clear_form()
        if type == "MethodCall":
            self.object_type_combo_box.show()
            self.method_combo_box.hide()
        elif type == "Choice":
            self.choice_form()
            self.object_type_combo_box.hide()
            self.method_combo_box.hide()
        else:
            self.object_type_combo_box.hide()
            self.method_combo_box.hide()

    def choice_form(self):
        def make_gb(title, type):
            gb = QGroupBox()
            gb.setTitle(title)
            layout = QVBoxLayout()
            layout.addWidget(type)
            gb.setLayout(layout)
            self.form_layout.addWidget(gb)
            return gb

        make_gb("Name of State", QLineEdit())

        layout = QVBoxLayout()
        choice_widget = QGroupBox()
        choice_widget.setTitle("Choices")
        edit_button = QPushButton("Edit")
        edit_button.setFixedSize(100, 20)
        edit_button.clicked.connect(self.choice_popup)
        layout.addWidget(edit_button)

        self.choice_list_widget = QListWidget()
        layout.addWidget(self.choice_list_widget)

        choice_widget.setLayout(layout)
        self.form_layout.addWidget(choice_widget)

        make_gb("Default", QLineEdit())

    def choice_popup(self):
        choice_popup = ChoicesPopup(self.payloads)
        if choice_popup.exec() == QDialog.DialogCode.Accepted:
            self.current_choices = choice_popup.get_input()
            self.update_list(self.choice_list_widget)

    def on_state_selected(self):
        object_type = self.object_type_combo_box.currentText()
        self.method_combo_box.clear()

        if object_type == "Custom":
            self.update_form(custom=True)
        else:
            methods = schema[object_type].keys()
            self.method_combo_box.addItems(methods)
            self.method_combo_box.show()

    def update_form(self, custom=False):
        if not custom:
            object_type = self.object_type_combo_box.currentText()
            method = self.method_combo_box.currentText()
            try:
                fields = schema[object_type][method]
            except KeyError:
                object_type = "Verification Case"
                method = "Initialize"
                fields = schema[object_type][method]

        self.clear_form()
        self.current_payloads = {}
        self.current_params = []

        def make_gb(title, type):
            gb = QGroupBox()
            gb.setTitle(title)
            layout = QVBoxLayout()
            layout.addWidget(type)
            gb.setLayout(layout)
            self.form_layout.addWidget(gb)
            return gb

        self.payload_combo_box = QComboBox()
        if self.payloads:
            payloads_formatted = [f"{item}" for item in self.payloads]
            payloads_formatted.insert(0, "")
            self.payload_combo_box.addItems(payloads_formatted)

        make_gb("Name of State", QLineEdit())

        if custom or method != "Initialize":
            make_gb("Object:", self.payload_combo_box)

        if custom:
            layout = QVBoxLayout()
            make_gb("MethodCall", QLineEdit())
            parameter_widget = QGroupBox()
            parameter_widget.setTitle("Parameters")
            parameter_button = QPushButton("Edit")
            parameter_button.setFixedSize(100, 20)
            parameter_button.clicked.connect(self.parameter_form)
            layout.addWidget(parameter_button)

            self.parameter_list_widget = QListWidget()
            layout.addWidget(self.parameter_list_widget)

            parameter_widget.setLayout(layout)
            self.form_layout.addWidget(parameter_widget)
        else:
            for field in fields:
                if field["type"] == "line_edit":
                    make_gb(field["label"], QLineEdit())
                elif field["type"] == "combo_box":
                    combo_box = QComboBox()
                    combo_box.addItems(["True", "False"])
                    make_gb(field["label"], combo_box)

        layout = QVBoxLayout()
        payload_widget = QGroupBox()
        payload_widget.setTitle("Payloads")
        layout.addWidget(self.payload_button)

        self.payload_list_widget = QListWidget()
        layout.addWidget(self.payload_list_widget)

        payload_widget.setLayout(layout)
        self.form_layout.addWidget(payload_widget)

        make_gb("Next", QLineEdit())

    def payload_form(self):
        payload_popup = ListPopup(self.current_payloads)
        if payload_popup.exec() == QDialog.DialogCode.Accepted:
            self.current_payloads = payload_popup.get_input()
            self.update_list(self.payload_list_widget)

    def parameter_form(self):
        popup = ListPopup(self.current_params, payload=False)
        if popup.exec() == QDialog.DialogCode.Accepted:
            self.params = popup.get_input()
            self.current_params = popup.get_input()
            self.update_list(self.parameter_list_widget)

    def update_list(self, list_widget):
        list_widget.clear()

        if list_widget == self.parameter_list_widget:
            to_add = self.current_params
            for input in to_add.keys():
                list_widget.addItem(input)
        elif list_widget == self.payload_list_widget:
            to_add = self.current_payloads
            for input in to_add.keys():
                list_widget.addItem(f"{input}: {to_add[input]}")
        else:
            to_add = self.current_choices
            for input in to_add:
                list_widget.addItem(
                    f"{input[0]}({input[1]}) equals {input[2]}: {input[3]}"
                )

    def clear_form(self):
        while self.form_layout.count() > 0:
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

    def save(self):
        self.form_data = {}

        type = self.type_combo_box.currentText()
        object_type = self.object_type_combo_box.currentText()
        method = self.method_combo_box.currentText()
        capitalized_keys = [
            "Type",
            "MethodCall",
            "Parameters",
            "Payloads",
            "Next",
            "Choices",
            "Default",
            "Title",
        ]

        self.form_data["Type"] = type
        if type == "MethodCall":
            if method == "Initialize":
                self.form_data["MethodCall"] = object_type
            else:
                method = (method.lower()).replace(" ", "_")
                object = self.payload_combo_box.currentText()
                self.form_data["MethodCall"] = f"Payloads['{object}'].{method}()"

        self.error = False

        self.form_data["Parameters"] = []

        for i in range(self.form_layout.count()):
            item = self.form_layout.itemAt(i).widget()
            parameter = item.title()

            if item.findChild(QLineEdit):
                text = item.findChild(QLineEdit).text()
            elif item.findChild(QComboBox):
                text = item.findChild(QComboBox).currentText()

            if not text:
                message = f"No input for {parameter}"
                self.send_error(message)
                self.error = True
                break

            if parameter == "Name of State":
                parameter = "Title"

            if parameter in capitalized_keys:
                self.form_data[parameter] = text
            elif not self.current_params:
                parameter = (parameter.lower()).replace(" ", "_")
                self.form_data["Parameters"].append({parameter: text})

        if not self.error:
            self.close()

    def send_error(self, text):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Error in State")
        error_msg.setText(text)
        error_msg.exec()

    def get_state(self):
        if self.current_payloads is not None and len(self.current_payloads) > 0:
            print(self.current_payloads)
            self.form_data["Payloads"] = self.current_payloads

        if self.current_params is not None and len(self.current_params) > 0:
            print(self.current_params)
            self.form_data["Parameters"] = self.current_params

        if self.current_choices is not None and len(self.current_choices) > 0:
            self.form_data["Choices"] = []
            for c in self.current_choices:
                if len(c) == 4:
                    method = (c[1].lower()).replace(" ", "_") + "()"
                    value = f"Payloads['{c[0]}'].{method}"
                    self.form_data["Choices"].append(
                        {"Value": value, "Equals": c[2], "Next": c[3]}
                    )
                elif len(c) == 3:
                    self.form_data["Choices"].append(
                        {"Value": c[0], "Equals": c[1], "Next": c[2]}
                    )

        return self.form_data


class ListPopup(QDialog):
    def __init__(self, input=None, payload=True):
        super().__init__()

        self.payload = payload

        self.initialize_ui()

        if payload:
            self.current_input = input if input else {}
        else:
            self.current_input = input if input else []

        self.populate_input_list()

    def initialize_ui(self):
        layout = QVBoxLayout()

        name_label = QLabel("Name:")
        self.name_line_edit = QLineEdit()

        if self.payload:
            self.setWindowTitle("Payloads")
            label = QLabel("Payload:")

            # Don't add name field if popup is not for payloads
            layout.addWidget(name_label)
            layout.addWidget(self.name_line_edit)
        else:
            self.setWindowTitle("Parameters")
            label = QLabel("Parameter:")

        self.line_edit = QLineEdit()

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

        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.input_list)
        layout.addWidget(add_button)
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
        self.input_dict = {}

        self.initialize_ui()

        self.populate_input_list()

    def initialize_ui(self):
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

        object_label = QLabel("Object")
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
        self.layout.addWidget(object_label)
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

    def populate_input_list(self):
        self.input_list.clear()

        if self.current_input:
            if len(self.current_input) == 3:
                for method, equals, next in self.current_input:
                    new_input = f"{method} equals {equals}: {next}"
            else:
                for object, method, equals, next in self.current_input:
                    new_input = f"{method}({object}) equals {equals}: {next}"
            self.input_dict[new_input] = self.current_input[0]
            self.input_list.addItem(new_input)

    def add_input(self):
        object = self.object_input.currentText()
        if object != "Custom":
            method = self.method_combo_box.currentText()
        else:
            method = self.method_input.text()
        equals = self.equals_input.currentText()
        next = self.next_input.text()

        if method and equals and next:
            if object:
                self.current_input.append((object, method, equals, next))
            else:
                self.current_input.append((method, equals, next))
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
        self.current_input.remove(self.input_dict[item.text()])
        self.input_dict.pop(item.text())
        self.populate_input_list()
        self.input_list.takeItem(self.input_list.row(item))

    def get_input(self):
        print(self.current_input)
        return self.current_input
