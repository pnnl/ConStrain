"""
Contained is the class for PopupWindow, the popup displayed when 'Add Basic' is chosen in the states tab.
"""

import json
import re
import os

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
    QSizePolicy,
    QLayout,
)
from PyQt6.QtGui import QPixmap

from constrain.app.list_and_choice_popups import ListPopup, ChoicesPopup

script_directory = os.path.dirname(os.path.abspath(__file__))
dependencies_path = os.path.join(script_directory, "dependencies.json")
api_to_method_path = os.path.join(script_directory, "api_to_method.json")

# mapping from object to its methods and its methods to its parameters for display in popup
with open(dependencies_path) as f:
    schema = json.load(f)

# mapping from object to its methods using the true method names
with open(api_to_method_path) as f:
    api_to_method = json.load(f)


class PopupWindow(QDialog):
    def __init__(self, payloads=[], state_names=[], rect=None, load=False):
        """Form to be displayed for user to edit or add a basic state

        Args:
            payloads (list): list of already-made objects to choose from when making a state
            state_names (list): list of already_made state names because state name in this popup must be unique
            rect (CustomItem): CustomItem associated with this popup
            load (bool): True if this popup is being created because of an import, false otherwise
        """
        super().__init__()

        # objects that this popup has created
        self.current_payloads = None

        # parameters that this popup has created (only used in Custom MethodCall type)
        self.current_params = None

        # choices that this popup has created (only used in Choice type)
        self.current_choices = None

        self.payloads = payloads

        self.state_names = state_names

        # dictionary that stores the state contained in this popup
        self.form_data = {}

        # stores whether or not the popup has an error
        self.error = False

        self.initialize_base_ui()
        self.set_ui() if not load else self.load_ui(rect)

    def initialize_base_ui(self):
        """Initializes UI that is used when both loading the popup and creating the popup"""
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
        """Loads UI for when user is manually adding information instead of importing"""
        self.setWindowTitle("Add State")

        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        self.type_combo_box.addItems(["", "MethodCall", "Choice"])

        # object types to choose from
        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")

        self.object_type_combo_box.addItems(object_types)

        layout.addWidget(self.type_combo_box)
        layout.addWidget(self.object_type_combo_box)
        layout.addWidget(self.method_combo_box)

        # hide until necessary
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
        """Given a MethodCall to be used in the API, this function returns the object and method from
        this MethodCall

        Args:
            call (str): MethodCall

        Returns:
            str: the object that the MethodCall uses, None if not found
            str: the method that the MethodCall uses, None if not found
        """
        object_pattern = r"Payloads\['(.*?)'\]"
        method_pattern = r"Payloads\['\w+'\]\.(\w+)"

        object_match = re.search(object_pattern, call)
        object = object_match.group(1) if object_match else None

        method_match = re.search(method_pattern, call)
        method = method_match.group(1) if method_match else None

        return object, method

    def get_api_from_method(self, method):
        """Given a method, returns its object type

        Args:
            method (str): a method in API format, i.e. 'get_library_items'

        Returns:
            str: an object type in API format, i.e. 'VerificationLibrary'
        """
        return next(
            (api for api, methods in api_to_method.items() if method in methods), None
        )

    def format_method(self, method):
        """Translates method in API format to popup format

        Args:
            method (str): a method in API format, i.e. 'get_library_items'

        Returns:
            str: a method in popup format, i.e. 'Get Library Items'
        """
        lowercase_words = ["of", "in"]
        result = " ".join(word.capitalize() for word in method.split("_"))

        result = result.replace("Json", "JSON")

        for word in lowercase_words:
            if " " + word + " " in result:
                result = result.replace(" " + word + " ", " " + word.lower() + " ")

        return result

    def set_state(self, to_set):
        """On import, fills form with text based on state that is passed to it

        Args:
            to_set (dict): state that is to be input into popup
        """

        # make list of keys with optional added to each parameter
        to_set_keys_with_optional = [
            f"{parameter} - Optional" for parameter in to_set.keys()
        ]

        # map list of keys with optional added to each parameter to its counterpart with optional added
        mapping = dict(zip(to_set_keys_with_optional, to_set.keys()))

        # for group boxes in self.form_layout, set text depending on title
        for i in range(self.form_layout.count()):
            item = self.form_layout.itemAt(i).widget()
            parameter = item.title()

            if parameter in mapping.keys():
                parameter = mapping[parameter]
            elif parameter not in to_set.keys():
                continue

            if item.findChild(QLineEdit):
                item.findChild(QLineEdit).setText(to_set[parameter])
            elif item.findChild(QComboBox):
                item.findChild(QComboBox).setCurrentText(to_set[parameter])

    def load_ui(self, rect):
        """Loads UI based on state of rect. Called when edit rect after import

        Args:
            rect (CustomItem): rect associated with self
        """

        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        state = rect.state
        self.type_combo_box.addItems(["", "MethodCall", "Choice"])
        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)

        type = state["Type"]
        if type == "MethodCall":
            self.load_method_ui(state, layout)
        elif type == "Choice":
            self.load_choice_ui(state, layout)
        else:
            return

    def load_choice_ui(self, state, layout):
        """Adds Choice UI to layout from self.load_ui given state and layout

        Args:
            state (dict): state of the CustomItem associated with self
            layout (PyQt6.QtWidgets.QVBoxLayout): base layout for this popup
        """

        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")

        title = state["Title"]

        # parameters to add in first layer of popup
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

        # add parameter values to first layer of popup
        self.set_state(parameters)

        # fill choice list widget with imported choices
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
        """Adds MethodCall UI to layout from self.load_ui given state and layout. Requires state['Type'] == 'MethodCall'

        Args:
            state (dict): state of the CustomItem associated with self
            layout (PyQt6.QtWidgets.QVBoxLayout): base layout for this popup
        """

        object_types = list(schema.keys())
        object_types.insert(0, "")
        object_types.append("Custom")

        type = state["Type"]
        title = state["Title"]
        self.type_combo_box.setCurrentText(type)

        # parameters to add in first layer of popup
        parameters = {}

        # payloads that this state creates
        current_payloads = {}

        method_call = state["MethodCall"]
        if "Payloads" in method_call:
            # non-initialization or possibly custom method
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
            # initialization method
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
            # certainly custom
            object_type = "Custom"
            parameters["MethodCall"] = method_call
            custom_parameters = state.get("Parameters", {})

        # set current_payloads
        if "Payloads" in state:
            current_payloads = {p: str(state["Payloads"][p]) for p in state["Payloads"]}

        # get "Next" from state, empty if there is none
        next_state = state.get("Next", "")

        self.object_type_combo_box.addItems(object_types)

        # select object type
        if object_type != "Custom":
            self.object_type_combo_box.setCurrentText(object_type)
            self.method_combo_box.show()
        else:
            # method combo box unnecessary
            self.method_combo_box.hide()

            self.object_type_combo_box.setCurrentText(object_type)
            self.method_combo_box.currentIndexChanged.connect(
                lambda: self.update_form(True)
            )

            # add params to list widget
            self.current_params = custom_parameters
            for item in custom_parameters:
                self.parameter_list_widget.addItem(item)

        self.method_combo_box.addItem("")

        # add methods if object is valid and not custom
        if object_type in schema:
            self.method_combo_box.addItems(schema[object_type])

        # set layout
        layout.addWidget(self.type_combo_box)
        layout.addWidget(self.object_type_combo_box)
        layout.addWidget(self.method_combo_box)

        layout.addLayout(self.form_layout)
        layout.addLayout(self.buttons_layout)

        self.type_combo_box.currentIndexChanged.connect(self.on_type_selected)
        self.object_type_combo_box.currentIndexChanged.connect(self.on_state_selected)

        # set method combo box
        if object_type != "Custom":
            self.method_combo_box.currentIndexChanged.connect(
                lambda: self.update_form(False)
            )
            self.method_combo_box.setCurrentText(method)

        # set base layer params
        parameters["Name of State"] = title
        parameters["Next"] = next_state
        self.set_state(parameters)

        # set payloads
        self.current_payloads = current_payloads
        for item in current_payloads.keys():
            self.payload_list_widget.addItem(f"{item}: {current_payloads[item]}")

    def edit_mode(self, payloads):
        """Called when CustomItem is clicked. Sets window title and updates payloads

        Args:
            payloads (list): list of payload names across all states
        """
        self.setWindowTitle("Edit State")
        self.payloads = payloads

    def on_type_selected(self):
        """Sets UI based on which state type is selected"""
        type = self.type_combo_box.currentText()
        self.clear_form()

        if type == "MethodCall":
            self.object_type_combo_box.show()
        elif type == "Choice":
            self.choice_form()
            self.object_type_combo_box.hide()
        else:
            self.object_type_combo_box.hide()
        self.method_combo_box.hide()

    def choice_form(self):
        """Sets UI for Choice type. Called when Choice is selected as object type"""
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
        """Creates a ChoicesPopup object. Called when Edit button is clicked in Choice UI"""

        # initialize popup
        choice_popup = ChoicesPopup(self.payloads, self.current_choices)

        # set self.current_choices and update list widget when popup is OK'ed
        if choice_popup.exec() == QDialog.DialogCode.Accepted:
            self.current_choices = choice_popup.get_input()
            self.update_list(self.choice_list_widget)

    def on_state_selected(self):
        """Sets UI based on which object type is selected"""
        object_type = self.object_type_combo_box.currentText()
        self.method_combo_box.clear()

        if object_type == "Custom":
            self.update_form(custom=True)
        elif object_type == "":
            type = self.type_combo_box.currentText()
            self.clear_form()
            self.type_combo_box.setCurrentText(type)
            self.object_type_combo_box.setCurrentText("")
            self.method_combo_box.hide()
        else:
            methods = schema[object_type].keys()
            self.method_combo_box.addItems(methods)
            self.method_combo_box.show()

    def make_and_add_groupbox(self, title, widget):
        """Creates and adds QGroupBox to layout with given title and widget

        Args:
            title (str): title to be displayed
            widget (PyQt6.QtWidgets.*): widget to be displayed

        Returns:
            PyQt6.QtWidgets.QGroupBox: groupbox created
        """
        gb = QGroupBox()
        gb.setTitle(title)
        layout = QVBoxLayout()

        # tt_label = QLabel()
        # pixmap = QPixmap("tt.png")
        # tt_label.setPixmap(pixmap)

        # layout.addWidget(tt_label)
        layout.addWidget(widget)
        gb.setLayout(layout)
        self.form_layout.addWidget(gb)
        return gb

    def update_custom_form(self):
        """Sets UI for when Custom object type is chosen"""

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
        """Sets UI based on which method is chosen

        Args:
            custom (bool): whether or not this is a custom object type
        """

        # need to first clear all data, if any, that was previously written in this popup
        self.clear_form()
        self.current_payloads = {}
        self.current_params = []

        object_type = self.object_type_combo_box.currentText()
        method = self.method_combo_box.currentText()

        # get fields needed for this method
        fields = schema.get(object_type, {}).get(method, [])

        # set possible objects to be chosen
        self.payload_combo_box = QComboBox()
        if self.payloads:
            payloads_formatted = [f"{item}" for item in self.payloads]
            payloads_formatted.insert(0, "")
            self.payload_combo_box.addItems(payloads_formatted)

        self.make_and_add_groupbox("Name of State", QLineEdit())

        # show object combo box only if popup is not an MethodCall initialization
        if custom or method != "Initialize":
            self.make_and_add_groupbox("Object", self.payload_combo_box)

        if custom:
            self.update_custom_form()
        else:
            # create groupboxes for each necessary field for the method
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
        """Creates a ListPopup object. Called when payload Edit button is clicked"""

        # pass in current_payloads in order to fill list widget in popup
        payload_popup = ListPopup(self.current_payloads)

        # set self.current_payloads and update list widget when popup is OK'ed
        if payload_popup.exec() == QDialog.DialogCode.Accepted:
            self.current_payloads = payload_popup.get_input()
            self.update_list(self.payload_list_widget)

    def parameter_form(self):
        """Creates a ListPopup object. Called when parameter Edit button is clicked"""

        # pass in current_params in order to fill list widget in popup
        popup = ListPopup(self.current_params, payload=False)

        # set self.current_params and update list widget when popup is OK'ed
        if popup.exec() == QDialog.DialogCode.Accepted:
            self.current_params = popup.get_input()
            self.update_list(self.parameter_list_widget)

    def update_list(self, list_widget):
        """Updates list widget with current values

        Args:
            list_widget (PyQt6.QtWidgets.QListWidget): list widget to update
        """

        # needed since values may be deleted in ListPopup or ChoicesPopup
        list_widget.clear()

        # search for what list widget it is and then update based on current values
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
        """Clears main form"""
        while self.form_layout.count() > 0:
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

    def save(self):
        """On click of save button, generates a dict containing the state"""

        # state
        self.form_data = {}

        # need to reset error
        self.error = False

        type = self.type_combo_box.currentText()
        object_type = self.object_type_combo_box.currentText()
        method = self.method_combo_box.currentText()

        # non-fields
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
                # get method format needed for API call
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

            # report error if necessary parameter is not filled
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
                        break

            # need 'Title' instead of 'Name of State' as key in final form
            if parameter == "Name of State":
                matching_names = [name for name in self.state_names if name == text]
                if (matching_names and not self.rect) or (
                    len(matching_names) == 2 and self.rect
                ):
                    self.send_error(f"{text} already exists")
                    break
                parameter = "Title"

            # retrieve only the field title
            if "Optional" in parameter:
                parameter = parameter.split(" - Optional")[0]

            if parameter in capitalized_keys:
                self.form_data[parameter] = text
            elif not self.current_params:
                parameter = (parameter.lower()).replace(" ", "_")
                self.form_data["Parameters"][parameter] = text

        # keep open if error
        if not self.error:
            self.close()

    def send_error(self, text):
        """Displays an error message with given text

        Args:
            text (str): text to be displayed
        """
        self.error = True
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Error in State")
        error_msg.setText(text)
        error_msg.exec()

    def get_state(self):
        """Returns compiled state of the popup

        Returns:
            dict: compiled state of the popup
        """
        if self.current_payloads and len(self.current_payloads) > 0:
            self.form_data["Payloads"] = self.current_payloads

        if self.current_params and len(self.current_params) > 0:
            self.form_data["Parameters"] = self.current_params

        if self.current_choices and len(self.current_choices) > 0:
            self.form_data["Choices"] = self.current_choices
        return self.form_data
