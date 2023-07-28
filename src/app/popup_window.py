from PyQt6.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QListWidget,
    QDialog,
    QGroupBox,
    QMessageBox,
)
import json
import re
from list_and_choice_popups import ListPopup, ChoicesPopup

with open("dependencies.json") as f:
    schema = json.load(f)

with open("api_to_method.json") as f:
    api_to_method = json.load(f)


class PopupWindow(QDialog):
    def __init__(self, payloads={}, rect=None, load=False):
        super().__init__()
        self.current_payloads = None
        self.current_params = None
        self.current_choices = None
        self.payloads = payloads
        self.form_data = {}
        self.error = False
        self.initialize_base_ui()
        self.set_ui() if not load else self.load_ui(rect)

    def initialize_base_ui(self):
        self.type_combo_box = QComboBox()
        self.object_type_combo_box = QComboBox()
        self.method_combo_box = QComboBox()
        self.form_layout = QVBoxLayout()

        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.payload_button = QPushButton("Edit")

        self.save_button.setFixedSize(100, 20)
        self.cancel_button.setFixedSize(100, 20)
        self.payload_button.setFixedSize(100, 20)

        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.close)
        self.payload_button.clicked.connect(self.payload_form)

        self.payload_list_widget = QListWidget()
        self.parameter_list_widget = QListWidget()

        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)

    def set_ui(self):
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
        layout.addLayout(self.buttons_layout)

        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)
        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)
        self.method_combo_box.currentIndexChanged.connect(
            lambda: self.update_form(False)
        )

    def get_object_method_from_call(self, call):
        object_pattern = r"Payloads\['(.*?)'\]"
        method_pattern = r"Payloads\['\w+'\]\.(\w+)"

        object_match = re.search(object_pattern, call)
        object = object_match.group(1) if object_match else None

        method_match = re.search(method_pattern, call)
        method = method_match.group(1) if method_match else None

        return object, method

    def get_api_from_method(self, method):
        return next(
            (api for api, methods in api_to_method.items() if method in methods), None
        )

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
        layout.addLayout(self.buttons_layout)
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
        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")

        type = state["Type"]
        title = state["Title"]
        self.type_combo_box.setCurrentText(type)

        parameters = {}
        current_payloads = {}

        if type == "MethodCall":
            method_call = state["MethodCall"]
            if "Payloads" in method_call:
                object, method = self.get_object_method_from_call(method_call)
                parameters["Object"] = object
                object_type = self.get_api_from_method(method)
                method = self.format_method(method)
                if "Parameters" in state.keys():
                    parameters.update(
                        {
                            self.format_method(p): str(state["Parameters"][p])
                            for p in state["Parameters"]
                        }
                    )
            elif method_call in schema.keys():
                object_type = method_call
                method = "Initialize"
                if "Parameters" in state.keys():
                    parameters.update(
                        {
                            self.format_method(p): str(state["Parameters"][p])
                            for p in state["Parameters"]
                        }
                    )
            else:
                object_type = "Custom"
                parameters["MethodCall"] = method_call
                custom_parameters = state.get("Parameters", {})

            if "Payloads" in state:
                current_payloads = {
                    p: str(state["Payloads"][p]) for p in state["Payloads"]
                }

            next_state = state.get("Next", "")

        self.object_type_combo_box.addItems(object_types)

        if object_type != "Custom":
            self.object_type_combo_box.setCurrentText(object_type)
        else:
            self.method_combo_box.hide()
            self.object_type_combo_box.setCurrentText(object_type)
            self.method_combo_box.currentIndexChanged.connect(
                lambda: self.update_form(True)
            )
            self.current_params = custom_parameters
            for item in custom_parameters:
                self.parameter_list_widget.addItem(item)

        self.method_combo_box.addItem("")
        if object_type in schema:
            self.method_combo_box.addItems(schema[object_type])

        layout.addWidget(self.type_combo_box)
        layout.addWidget(self.object_type_combo_box)
        layout.addWidget(self.method_combo_box)

        layout.addLayout(self.form_layout)
        layout.addLayout(self.buttons_layout)

        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)
        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)

        if object_type != "Custom":
            self.method_combo_box.currentIndexChanged.connect(
                lambda: self.update_form(False)
            )
            self.method_combo_box.setCurrentText(method)

        parameters["Name of State"] = title
        parameters["Next"] = next_state
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
        self.make_and_add_groupbox("Name of State", QLineEdit())

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

        self.make_and_add_groupbox("Default", QLineEdit())

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

    def make_and_add_groupbox(self, title, widget):
        gb = QGroupBox()
        gb.setTitle(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        gb.setLayout(layout)
        self.form_layout.addWidget(gb)
        return gb

    def update_custom_form(self):
        layout = QVBoxLayout()

        self.make_and_add_groupbox("MethodCall", QLineEdit())

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

    def update_form(self, custom=False):
        self.clear_form()
        self.current_payloads = {}
        self.current_params = []

        object_type = self.object_type_combo_box.currentText()
        method = self.method_combo_box.currentText()
        fields = schema.get(object_type, {}).get(method, [])

        if not custom and not fields:
            object_type = "Verification Case"
            method = "Initialize"
            fields = schema.get(object_type, {}).get(method, [])

        self.payload_combo_box = QComboBox()
        if self.payloads:
            payloads_formatted = [f"{item}" for item in self.payloads]
            payloads_formatted.insert(0, "")
            self.payload_combo_box.addItems(payloads_formatted)

        self.make_and_add_groupbox("Name of State", QLineEdit())

        if custom or method != "Initialize":
            self.make_and_add_groupbox("Object", self.payload_combo_box)

        if custom:
            self.update_custom_form()
        else:
            for field in fields:
                if field["type"] == "line_edit":
                    self.make_and_add_groupbox(field["label"], QLineEdit())
                elif field["type"] == "combo_box":
                    combo_box = QComboBox()
                    combo_box.addItems(["", "True", "False"])
                    self.make_and_add_groupbox(field["label"], combo_box)

        payload_widget = QGroupBox()
        payload_widget.setTitle("Payloads")
        layout = QVBoxLayout()

        self.payload_button = QPushButton("Edit")
        self.payload_button.setFixedSize(100, 20)
        self.payload_button.clicked.connect(self.payload_form)
        layout.addWidget(self.payload_button)

        self.payload_list_widget = QListWidget()
        layout.addWidget(self.payload_list_widget)

        payload_widget.setLayout(layout)
        self.form_layout.addWidget(payload_widget)

        self.make_and_add_groupbox("Next - Optional", QLineEdit())

    def payload_form(self):
        payload_popup = ListPopup(self.current_payloads)
        if payload_popup.exec() == QDialog.DialogCode.Accepted:
            self.current_payloads = payload_popup.get_input()
            self.update_list(self.payload_list_widget)

    def parameter_form(self):
        popup = ListPopup(self.current_params, payload=False)
        if popup.exec() == QDialog.DialogCode.Accepted:
            self.current_params = popup.get_input()
            self.update_list(self.parameter_list_widget)

    def update_list(self, list_widget):
        list_widget.clear()

        if list_widget == self.parameter_list_widget:
            to_add = self.current_params
            for input in to_add:
                list_widget.addItem(input)
        elif list_widget == self.payload_list_widget:
            to_add = self.current_payloads
            for input in to_add.keys():
                list_widget.addItem(f"{input}: {to_add[input]}")
        else:
            to_add = self.current_choices
            for input in to_add:
                list_widget.addItem(
                    f"{input['Value']} = {input['Equals']} -> {input['Next']}"
                )

    def clear_form(self):
        while self.form_layout.count() > 0:
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

    def save(self):
        self.form_data = {}
        self.error = False

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

        self.form_data["Parameters"] = {}

        for i in range(self.form_layout.count()):
            item = self.form_layout.itemAt(i).widget()
            parameter = item.title()

            if item.findChild(QLineEdit):
                text = item.findChild(QLineEdit).text()
            elif item.findChild(QComboBox):
                text = item.findChild(QComboBox).currentText()

            if not text or text == "":
                if "Optional" in parameter:
                    continue
                else:
                    if (
                        parameter != "Payloads"
                        and parameter != "Object"
                        and parameter != "Parameters"
                    ):
                        self.send_error(f"{parameter} field is empty")
                        self.error = True
                        break

            if parameter == "Name of State":
                parameter = "Title"

            if parameter in capitalized_keys:
                self.form_data[parameter] = text
            elif not self.current_params:
                parameter = (parameter.lower()).replace(" ", "_")
                self.form_data["Parameters"][parameter] = text

        if not self.error:
            self.close()

    def send_error(self, text):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Error in State")
        error_msg.setText(text)
        error_msg.exec()

    def get_state(self):
        if self.current_payloads and len(self.current_payloads) > 0:
            self.form_data["Payloads"] = self.current_payloads

        if self.current_params and len(self.current_params) > 0:
            self.form_data["Parameters"] = self.current_params

        if self.current_choices and len(self.current_choices) > 0:
            self.form_data["Choices"] = self.current_choices
        return self.form_data
