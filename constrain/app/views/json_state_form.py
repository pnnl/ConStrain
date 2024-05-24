import json

from PyQt6 import QtWidgets, QtGui

from constrain.app.utils import utils


class JSONStateForm(QtWidgets.QDialog):
    def __init__(self, rect=None, edit=False) -> None:
        """JSONStateForm is a QDialog for users to make states which contain the entire json definition
        for the state in a TextEdit

        Args:
            rect (CustomItem): the CustomItem that this state form is assigned to. If rect is passed, JSONStateForm
            will load the state of the rect into its TextEdit

            edit (bool): Don't think this is necessary. Specifies whether or not a rect's state is being edited
        """
        super().__init__()

        # value to say whether the state form has any errors
        self.error = False

        # layout
        form_layout = QtWidgets.QVBoxLayout()
        state_label = QtWidgets.QLabel("State:")

        if edit:
            self.setWindowTitle("Edit State")
        else:
            self.setWindowTitle("Add State")

        # text edit where the user will type in the json
        self.state_input = QtWidgets.QTextEdit()
        if rect:
            self.state_input.setText(rect.get_state_string())

        # make it so that tab equals 4 spaces
        font = self.state_input.font()
        fontMetrics = QtGui.QFontMetricsF(font)
        spaceWidth = fontMetrics.horizontalAdvance(" ")
        self.state_input.setTabStopDistance(spaceWidth * 4)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.check_state)

        # finalize layout
        form_layout.addWidget(state_label)
        form_layout.addWidget(self.state_input, 3)
        form_layout.addWidget(self.save_button)

        self.setLayout(form_layout)

    def get_state(self) -> dict:
        """Retrieves input state from self.

        Returns:
            dict: a json dictionary containing the input state in json format
        """
        state_text = self.state_input.toPlainText()

        try:
            state_json = json.loads(state_text)
        except json.decoder.JSONDecodeError:
            # return None if dict is not correctly loaded
            return None

        # since we need Title to be a key for other processes, have to convert the dict
        if state_json:
            if len(state_json.keys()) > 1:
                return None
            else:
                title = [key for key in state_json.keys()][0]
                state_json = state_json[title]
                state_json["Title"] = title
        return state_json

    def check_state(self) -> None:
        """Performs basic validity checks on the state form, setting self.error as True and displaying
        an error popup if any checks are failed
        """
        self.error = False
        state = self.get_state()

        if not state:
            utils.send_error("Error in State", "Invalid state format")
            self.error = True
        else:
            state_type = state.get("Type")

            if state_type not in ["Choice", "MethodCall"]:
                self.error = True
                utils.send_error("Error in State", "Invalid state type")
            elif state_type == "Choice":
                if "Choices" not in state:
                    self.error = True
                    utils.send_error(
                        "Error in State", "Choice type, but no Choices key"
                    )
                elif any(key in state for key in ("Start", "End")):
                    self.error = True
                    utils.send_error(
                        "Error in State", "Start/End keys not allowed in a Choice type"
                    )
                else:
                    self.close()
            else:
                if all(key in state for key in ("Start", "End")):
                    self.error = True
                    utils.send_error(
                        "Error in State",
                        "Cannot have both Start and End keys in a state",
                    )

                if state.get("End") and state.get("Next"):
                    self.error = True
                    utils.send_error(
                        "Error in State", "State has 'End' and 'Next' keys"
                    )
