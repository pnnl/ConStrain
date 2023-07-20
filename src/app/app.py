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
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from import_form import ImportForm
from meta_form import MetaForm
from workflow_diagram import WorkflowDiagram
from rect_connect import CustomItem
import json


with open("dependencies.json") as file:
    data = json.load(file)

form = {}


class GUI(QMainWindow):
    def __init__(self, setting):
        """QMainWindow to contain MetaForm, ImportForm, and Workflow Diagram.

        Args:
            setting: (optional)
        """
        super().__init__()
        self.initialize_ui(setting)

    def initialize_ui(self, setting):
        self.setWindowTitle("ConStrain")

        self.meta_form = MetaForm()
        self.import_form = ImportForm()
        self.states_form = WorkflowDiagram(setting)

        self.column_list = QListWidget()
        self.column_list.addItems(["Meta", "Imports", "State"])
        self.column_list.currentItemChanged.connect(self.display_form)

        self.column_frame = QFrame()
        self.column_frame.setFrameStyle(QFrame.Shape.NoFrame)
        self.column_frame.setMaximumWidth(100)
        column_layout = QVBoxLayout()
        column_layout.addWidget(self.column_list)
        self.column_frame.setLayout(column_layout)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.column_frame)
        middle_layout.addWidget(self.meta_form)
        middle_layout.addWidget(self.import_form)
        middle_layout.addWidget(self.states_form)

        self.validate_button = QPushButton("Validate")
        self.validate_button.setFixedSize(100, 20)
        self.validate_button.clicked.connect(self.validate_form)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setEnabled(False)
        self.submit_button.setFixedSize(100, 20)
        self.submit_button.clicked.connect(self.submit_form)

        buttons = QHBoxLayout()
        buttons.addWidget(self.validate_button)
        buttons.addWidget(self.submit_button)
        buttons.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(buttons)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.initialize_toolbar()

    def initialize_toolbar(self):
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
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Select a JSON File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, "r") as f:
                workflow = json.load(f)
                if isinstance(workflow, dict):
                    self.meta_form.read_import(
                        workflow.get("workflow_name"), workflow.get("meta")
                    )
                    self.import_form.read_import(workflow.get("imports"))
                    self.states_form.read_import(workflow.get("states"))
                    self.get_workflow()
                else:
                    print("error")

    def display_form(self, current_item):
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

    def create_json(self, workflow):
        data = {
            "workflow_name": self.meta_form.get_workflow_name(),
            "meta": self.meta_form.get_meta(),
            "imports": self.import_form.get_imports(),
            "states": {},
        }
        for item in workflow:
            copy_item = dict(item)
            title = copy_item.pop("Title")
            data["states"][title] = copy_item
        json_data = data
        return json_data

    def submit_form(self):
        self.submit_button.setEnabled(False)

    def get_workflow(self):
        items = [
            item
            for item in self.states_form.scene.items()
            if isinstance(item, CustomItem)
        ]
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

        def dfs_helper(item, path):
            path.append(item)
            visited.add(item)

            if item not in items or not item.children:
                item.setBrush("red")
                item.state["End"] = "True"
                paths.append(path[:])
            else:
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
        for path in paths:
            for node in path:
                if node not in visited:
                    workflow_path.append(node.state)
                    visited.add(node)
        return workflow_path

    def validate_form(self, data):
        workflow_path = self.get_workflow()
        json_data = self.create_json(workflow_path)
        valid = True
        if valid:
            self.submit_button.setEnabled(True)


class UserSetting(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ConStrain")
        query = QLabel("Advanced or basic user settings?")
        self.advanced_button = QPushButton("Advanced")
        self.advanced_button.clicked.connect(self.showAdvanced)
        self.basic_button = QPushButton("Basic")
        self.basic_button.clicked.connect(self.showBasic)

        form_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.advanced_button)
        button_layout.addWidget(self.basic_button)

        form_layout.addWidget(query)
        form_layout.addLayout(button_layout)

        self.setLayout(form_layout)

    def showBasic(self):
        self.close()
        self.gui = GUI("basic")
        self.gui.show()

    def showAdvanced(self):
        self.close()
        self.gui = GUI("advanced")
        self.gui.show()


app = QApplication(sys.argv)

window = UserSetting()
window.show()

sys.exit(app.exec())
