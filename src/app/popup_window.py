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
import time

with open("dependencies.json") as f:
    schema = json.load(f)

with open("api_to_method.json") as f:
    api_to_method = json.load(f)


class PopupWindow(QDialog):
    def __init__(self, payloads={}, rect=None, edit=False, state=None, load=False):
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

        if not load:
            self.initialize_ui()
        else:
            self.load_ui(rect)

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

    def get_object_method_from_call(self, call):
        print(call)
        object_pattern = r"Payloads\['(.*?)'\]"
        method_pattern = r"Payloads\['\w+'\]\.(\w+)"

        object_match = re.search(object_pattern, call)
        if object_match:
            object = object_match.group(1)
        else:
            object = None

        method_match = re.search(method_pattern, call)
        if method_match:
            method = method_match.group(1)
        else:
            method = None

        return object, method

    def get_api_from_method(self, method):
        for api in api_to_method.keys():
            if method in api_to_method[api]:
                return api
        return None

    def format_method(self, method):
        lowercase_words = ["of", "in"]
        result = " ".join(word.capitalize() for word in method.split("_"))

        result = result.replace("Json", "JSON")

        for word in lowercase_words:
            if " " + word + " " in result:
                result = result.replace(" " + word + " ", " " + word.lower() + " ")

        return result

    def set_state(self, to_set):
        for i in range(self.form_layout.count()):
            item = self.form_layout.itemAt(i).widget()
            parameter = item.title()
            if parameter in to_set.keys():
                if item.findChild(QLineEdit):
                    item.findChild(QLineEdit).setText(to_set[parameter])
                elif item.findChild(QComboBox):
                    item.findChild(QComboBox).setCurrentText(to_set[parameter])

    def load_ui(self, rect):
        self.setWindowTitle("Add State")

        layout = QVBoxLayout()
        self.setLayout(layout)

        state = rect.state
        self.type_combo_box.addItems(["", "MethodCall", "Choice"])

        type = state["Type"]
        if type == "MethodCall":
            self.load_method_ui(state, layout)
        elif type == "Choice":
            self.load_choice_ui(state, layout)
        else:
            return

    def load_choice_ui(self, state, layout):
        layout = layout
        state = state

        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")
        title = state["Title"]

        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)
        parameters = {}

        if "Choices" in state.keys():
            self.current_choices = state["Choices"]

        if "Default" in state.keys():
            parameters["Default"] = state["Default"]

        parameters["Name of State"] = title

        layout.addWidget(self.type_combo_box)
        self.type_combo_box.setCurrentText("Choice")
        layout.addLayout(self.form_layout)
        layout.addLayout(self.buttons)
        self.set_state(parameters)

        for choice in self.current_choices:
            object, method = self.get_object_method_from_call(choice["Value"])
            if not object or not method:
                method = choice["Value"]
                object = ""
                widget_line = f"{method} = {choice['Equals']} -> {choice['Next']}"
            else:
                widget_line = (
                    f"{method}({object}) = {choice['Equals']} -> {choice['Next']}"
                )
            self.choice_list_widget.addItem(widget_line)

    def load_method_ui(self, state, layout):
        layout = layout
        state = state

        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")
        type = state["Type"]
        title = state["Title"]
        self.type_combo_box.setCurrentText(type)
        parameters = {}
        current_payloads = {}
        if type == "MethodCall":
            if "Payloads" in state["MethodCall"]:
                # if regular method call
                object, method = self.get_object_method_from_call(state["MethodCall"])
                parameters["Object"] = object
                object_type = self.get_api_from_method(method)
                method = self.format_method(method)
                if "Parameters" in state.keys():
                    for p in state["Parameters"]:
                        parameters[self.format_method(p)] = str(state["Parameters"][p])
                # state["Object"] = object

            elif state["MethodCall"] in [api.replace(" ", "") for api in schema.keys()]:
                # if initialization
                object_type = re.sub(r"([a-z])([A-Z])", r"\1 \2", state["MethodCall"])
                method = "Initialize"
                if "Parameters" in state.keys():
                    for p in state["Parameters"]:
                        parameters[self.format_method(p)] = str(state["Parameters"][p])
            else:
                # if custom
                object_type = "Custom"
                # if "Parameters" in state.keys():
                # parameters = state["Parameters"]
                parameters["MethodCall"] = state["MethodCall"]
                custom_parameters = state["Parameters"]

            if "Payloads" in state.keys():
                for p in state["Payloads"]:
                    current_payloads[p] = str(state["Payloads"][p])

            next = ""
            if "Next" in state.keys():
                next = state["Next"]

        self.object_type_combo_box.addItems(object_types)

        self.method_combo_box.addItem("")
        if object_type != "Custom":
            self.object_type_combo_box.setCurrentText(object_type)
        else:
            self.method_combo_box.hide()

        if object_type in schema.keys():
            self.method_combo_box.addItems(schema[object_type])

        layout.addWidget(self.type_combo_box)
        layout.addWidget(self.object_type_combo_box)
        layout.addWidget(self.method_combo_box)

        layout.addLayout(self.form_layout)
        layout.addLayout(self.buttons)

        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)
        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)

        if object_type != "Custom":
            self.method_combo_box.currentIndexChanged.connect(
                lambda: self.update_form(False)
            )
            self.method_combo_box.setCurrentText(method)
        else:
            self.object_type_combo_box.setCurrentText(object_type)
            self.method_combo_box.currentIndexChanged.connect(
                lambda: self.update_form(True)
            )
            self.current_params = custom_parameters
            for item in custom_parameters:
                self.parameter_list_widget.addItem(item)

        parameters["Name of State"] = title
        parameters["Next"] = next
        self.set_state(parameters)
        self.current_payloads = current_payloads
        for item in current_payloads.keys():
            self.payload_list_widget.addItem(f"{item}: {current_payloads[item]}")

    def edit_mode(self, payloads, rect, load=False):
        self.setWindowTitle("Edit State")
        self.payloads = payloads

        if not load and self.payloads:
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
        choice_popup = ChoicesPopup(self.payloads, self.current_choices)
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
            make_gb("Object", self.payload_combo_box)

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
                    f"{input[1]}({input[0]}) = {input[2]} -> {input[3]}"
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
                self.form_data["MethodCall"] = f"Payloads['{object}'].{method}"

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
                # self.send_error(message)
                # self.error = True
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
            self.form_data["Payloads"] = self.current_payloads

        if self.current_params is not None and len(self.current_params) > 0:
            self.form_data["Parameters"] = self.current_params

        if self.current_choices is not None and len(self.current_choices) > 0:
            print(self.current_choices)
            print(type(self.current_choices))
            self.form_data["Choices"] = []
            for c in self.current_choices:
                self.form_data["Choices"].append(c)
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

    def get_object_method_from_call(self, call):
        print(call)
        object_pattern = r"Payloads\['(.*?)'\]"
        method_pattern = r"Payloads\['\w+'\]\.(\w+)"

        object_match = re.search(object_pattern, call)
        if object_match:
            object = object_match.group(1)
        else:
            object = None

        method_match = re.search(method_pattern, call)
        if method_match:
            method = method_match.group(1)
        else:
            method = None

        return object, method

    def populate_input_list(self):
        self.input_list.clear()

        for choice in self.current_input:
            object, method = self.get_object_method_from_call(choice["Value"])
            if not object or not method:
                method = choice["Value"]
                object = ""
                widget_line = f"{method} = {choice['Equals']} -> {choice['Next']}"
            else:
                widget_line = f"Payloads['{object}'].{method} = {choice['Equals']} -> {choice['Next']}"
            self.input_list.addItem(widget_line)

    def add_input(self):
        object = self.object_input.currentText()
        if object != "Custom":
            method = self.method_combo_box.currentText()
        else:
            method = self.method_input.text()
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
        item = self.input_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)

        delete_action.triggered.connect(lambda: self.delete_input(item))

        menu.addAction(delete_action)

        menu.exec(self.input_list.mapToGlobal(position))

    def delete_input(self, item):
        self.populate_input_list()
        self.input_list.takeItem(self.input_list.row(item))

    def get_input(self):
        return self.current_input
