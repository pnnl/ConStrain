import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QFrame,
    QDialog,
    QLabel,
    QToolBar,
    QMenu,
    QFileDialog,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEventLoop
from PyQt6.QtGui import QAction
from import_form import ImportForm
from meta_form import MetaForm
from workflow_diagram import WorkflowDiagram
from rect_connect import CustomItem
import json
from src.api.workflow import Workflow
import warnings
import sys


class GUI(QMainWindow):
    def __init__(self, setting):
        """QMainWindow to contain MetaForm, ImportForm, and Workflow Diagram.

        Args:
            setting: (optional but should be sys.argv)
        """
        super().__init__()
        self.initialize_ui(setting)

    def initialize_ui(self, setting):
        self.setWindowTitle("ConStrain")

        self.meta_form = MetaForm()
        self.import_form = ImportForm()
        self.states_form = WorkflowDiagram(setting)

        # list containing meta, imports, and state for display on LHS
        self.column_list = QListWidget()
        self.column_list.addItems(["Meta", "Imports", "State"])
        self.column_list.currentItemChanged.connect(self.display_form)
        self.column_list.setStyleSheet(
            "QListWidget::item:selected { background-color: #145369; }"
        )
        self.column_list.setCurrentItem(self.column_list.item(0))

        # make and reposition frame containing meta, imports, and state
        self.column_frame = QFrame()
        self.column_frame.setFrameStyle(QFrame.Shape.NoFrame)
        self.column_frame.setFixedWidth(100)
        self.column_frame.setFixedHeight(76)
        self.column_frame.setStyleSheet(
            "background-color: #f0f0f0; border: 0px solid #f0f0f0;"
        )
        column_layout = QVBoxLayout()
        column_layout.addWidget(self.column_list)
        column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.column_frame.setLayout(column_layout)
        self.column_frame_container = QVBoxLayout()
        self.column_frame_container.addWidget(self.column_frame)
        self.column_frame_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        # layouts that are displayed when meta, imports, or state is selected
        middle_layout = QHBoxLayout()
        middle_layout.addLayout(self.column_frame_container)
        middle_layout.addWidget(self.meta_form)
        middle_layout.addWidget(self.import_form)
        middle_layout.addWidget(self.states_form)

        # validate and submit buttons
        self.validate_button = QPushButton("Validate")
        self.validate_button.setFixedSize(100, 20)
        self.validate_button.clicked.connect(self.validate_form)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setEnabled(False)
        self.submit_button.setFixedSize(100, 20)
        self.submit_button.clicked.connect(self.submit_form)

        # group validate and submit buttons
        buttons = QHBoxLayout()
        buttons.addWidget(self.validate_button)
        buttons.addWidget(self.submit_button)
        buttons.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # set layout for entire window
        main_layout = QVBoxLayout()
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(buttons)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.initialize_toolbar()

    def initialize_toolbar(self):
        """Creates toolbar to give option for importing .json and exporting .json"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        file_menu = QMenu("File", self)

        import_action = QAction("Import", self)
        import_action.triggered.connect(self.importFile)
        file_menu.addAction(import_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.exportFile)
        file_menu.addAction(export_action)

        toolbar.addAction(file_menu.menuAction())

    def exportFile(self):
        """Exports current state as a .json to local storage"""
        fp, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)"
        )

        if fp:
            try:
                workflow = self.get_workflow()
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(self.create_json(workflow), f, indent=4)
            except Exception:
                print("error")

    def importFile(self):
        """Imports a .json file to use a state and loads file into the GUI"""
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Select a JSON File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, "r") as f:
                workflow = json.load(f)
                if isinstance(workflow, dict):
                    # have each tab fill in the data
                    self.meta_form.read_import(
                        workflow.get("workflow_name"), workflow.get("meta")
                    )
                    self.import_form.read_import(workflow.get("imports"))
                    self.states_form.read_import(workflow.get("states"))
                    self.get_workflow()
                else:
                    # error if selected file cannot be converted to a dict
                    print("error")

    def display_form(self, current_item):
        """Displays tab that is selected

        Args:
            current_item (str): Name of tab (can be 'Meta', 'Imports', or 'State')
        """
        if current_item.text() == self.column_list.item(0).text():
            self.meta_form.show()
            self.import_form.hide()
            self.states_form.hide()
        elif current_item.text() == self.column_list.item(1).text():
            self.meta_form.hide()
            self.import_form.show()
            self.states_form.hide()
        else:
            self.meta_form.hide()
            self.import_form.hide()
            self.states_form.show()

    def create_json(self, states):
        """Collects information from all tabs in order to build a final .json

        Args:
            states (dict): The list of current states

        Returns:
            dict: The finalized .json file
        """
        data = {
            "workflow_name": self.meta_form.get_workflow_name(),
            "meta": self.meta_form.get_meta(),
            "imports": self.import_form.get_imports(),
            "states": {},
        }

        # Since each state contains its own name, and isn't a key in data['states'][name], we must make it so it
        # is a key to this dict
        for item in states:
            copy_item = dict(item)
            title = copy_item.pop("Title")
            data["states"][title] = copy_item
        json_data = data
        return json_data

    def submit_form(self):
        """Workflow for submitting the state. Triggered on the click of the Submit button. Displays a popup which
        shows the progress of running the state.
        """
        states = self.get_workflow()
        json_data = self.create_json(states)

        popup = SubmitPopup()

        # make worker a GUI attribute to not block the rest of the application
        self.worker = Worker(json_data)
        self.worker.update_text.connect(popup.update_text)

        self.worker.start()
        popup.exec()

    def get_workflow(self):
        """Organizes the states into a single list, colors states based on placing, returns organized workflow

        Returns:
            list: A compiled version of the state dicts in DFS order
        """

        # find all CustomItems in the scene
        items = [
            item
            for item in self.states_form.scene.items()
            if isinstance(item, CustomItem)
        ]

        # prepare for DFS
        roots = []
        for i in items:
            parent = True
            for j in items:
                if i in j.children:
                    parent = False
                    break
            if parent:
                roots.append(i)
                visited = set()

        paths = []

        # DFS helper method
        def dfs_helper(item, path):
            path.append(item)
            visited.add(item)

            if item not in items or not item.children:
                # item is a leaf node
                item.setBrush("red")
                item.state["End"] = "True"
                paths.append(path[:])
            else:
                # item is not a leaf node
                item.setBrush()

            for child in item.children:
                if child not in visited:
                    dfs_helper(child, path)

            path.pop()
            visited.remove(item)

        for root in roots:
            root.state["Start"] = "True"
            self.states_form.view.arrange_tree(root, 0, 0, 150)
            if root not in visited:
                dfs_helper(root, [])
            root.setBrush("green")

        workflow_path = []
        visited = set()

        # create final path through workflow
        for path in paths:
            for node in path:
                if node not in visited:
                    workflow_path.append(node.state)
                    visited.add(node)
        return workflow_path

    def validate_form(self):
        """Workflow for validating the state. Triggered on the click of the Validate button. Enables the submit
        button if the workflow is validated.
        """
        workflow_path = self.get_workflow()
        json_data = self.create_json(workflow_path)

        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=ResourceWarning)

        validate_wf = Workflow(json_data)
        valid = validate_wf.validate(verbose=True)
        if valid:
            self.submit_button.setEnabled(True)


class UserSetting(QDialog):
    def __init__(self):
        """QDialog to ask whether user wants Basic or Advanced settings in creating the workflow. Users
        are still able to add basic or advanced popups, but this diagram changes what is displayed on edit.
        Some rethinking about it may be necessary. Runs the GUI based on the setting chosen
        """
        super().__init__()
        self.setWindowTitle("ConStrain")
        query = QLabel("Advanced or basic user settings?")

        # buttons
        self.advanced_button = QPushButton("Advanced")
        self.advanced_button.clicked.connect(self.showAdvanced)
        self.basic_button = QPushButton("Basic")
        self.basic_button.clicked.connect(self.showBasic)

        # add buttons and query to layout
        form_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.advanced_button)
        button_layout.addWidget(self.basic_button)

        form_layout.addWidget(query)
        form_layout.addLayout(button_layout)

        self.setLayout(form_layout)

    def showBasic(self):
        """Displays basic GUI on selection"""
        self.close()
        self.gui = GUI("basic")
        self.gui.show()

    def showAdvanced(self):
        """Displays advanced GUI on selection"""
        self.close()
        self.gui = GUI("advanced")
        self.gui.show()


class Worker(QThread):
    update_text = pyqtSignal(str)

    def __init__(self, json_data):
        """Given the finalized workflow, creates a thread that runs the workflow in the Workflow API

        Args:
            json_data (dict): The finalized, json formatted dict of information from each tab
        """
        super(Worker, self).__init__()
        self.json_data = json_data

    def run(self):
        """Runs the thread"""

        # captures sys.stdout in an EmittingStream object to display in a popup
        sys.stdout = EmittingStream(self.update_text)

        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=ResourceWarning)

        # creates and runs the workflow based on the workflow provided
        wf = Workflow(self.json_data)
        wf.run_workflow(verbose=True)


class EmittingStream:
    def __init__(self, signal):
        self._signal = signal

    def write(self, message):
        # emits the signal with the message to update the QTextEdit
        # QMetaObject.invokeMethod(self._signal, "emit", Q_ARG(str, message.strip()))
        self._signal.emit(message.strip())

    def flush(self):
        pass


class SubmitPopup(QDialog):
    def __init__(self):
        """Creates a read-only popup containing the verbose run through Workflow"""
        super(SubmitPopup, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(400, 500)
        self.setWindowTitle("Results")
        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

    def update_text(self, message):
        self.text_edit.append(message)


app = QApplication(sys.argv)

window = UserSetting()
window.show()

sys.exit(app.exec())
