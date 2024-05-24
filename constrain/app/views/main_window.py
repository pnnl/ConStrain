import warnings
import json
import os

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QFrame,
    QToolBar,
    QMenu,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QAction, QPixmap, QPainter, QColor, QIcon

from constrain.app.views.import_form import ImportForm
from constrain.app.views.meta_form import MetaForm
from constrain.app.views.workflow_diagram import WorkflowDiagram
from constrain.app.views.submission_dialog import SubmissionDialog
from constrain.app.controllers.submit import Worker
from constrain.app.utils import utils
from constrain.api.workflow import Workflow


class MainWindow(QMainWindow):
    def __init__(self):
        """QMainWindow to contain MetaForm, ImportForm, and Workflow Diagram."""

        super().__init__()
        self.initialize_ui()

    def initialize_ui(self):
        self.setWindowTitle("ConStrain")

        self.meta_form = MetaForm()
        self.import_form = ImportForm()
        self.states_form = WorkflowDiagram("basic")

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
        validate_button = QPushButton("Validate")
        validate_button.setToolTip("Validate workflow")
        validate_button.setFixedSize(100, 23)
        validate_button.clicked.connect(self.validate_form)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setToolTip("Submit workflow")
        # self.submit_button.setEnabled(False)
        self.submit_button.setFixedSize(100, 23)
        self.submit_button.clicked.connect(self.submit_form)

        # group validate and submit buttons
        buttons = QHBoxLayout()
        # buttons.addWidget(validate_button)
        buttons.addWidget(self.submit_button)
        buttons.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # set layout for entire window
        main_layout = QVBoxLayout()
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(buttons)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        current_directory = os.path.dirname(os.path.abspath(__file__))
        icon_asset_path = os.path.join(
            current_directory, "../resources/images/strainer.png"
        )
        self.setWindowIcon(QIcon(icon_asset_path))

        self.initialize_toolbar()

    def initialize_toolbar(self):
        """Creates toolbar to give option for importing .json and exporting .json"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        file_menu = QMenu("File", self)

        import_action = QAction("Import Workflow", self)
        import_action.triggered.connect(self.import_file)
        file_menu.addAction(import_action)

        export_menu = QMenu("Export Workflow", self)
        file_menu.addMenu(export_menu)

        json_export_action = QAction("JSON", self)
        json_export_action.triggered.connect(self.export_file)
        export_menu.addAction(json_export_action)

        png_export_action = QAction("PNG", self)
        png_export_action.triggered.connect(self.export_as_png)
        export_menu.addAction(png_export_action)

        settings_menu = QMenu("Settings", self)
        state_form_settings_menu = QMenu("State Form Settings", self)

        self.basic_action = QAction("Basic Form", self, checkable=True)
        self.basic_action.triggered.connect(self.select_basic_state_form_setting)
        state_form_settings_menu.addAction(self.basic_action)
        self.basic_action.setChecked(True)

        self.json_form_setting_select = QAction("JSON Form", self, checkable=True)
        self.json_form_setting_select.triggered.connect(
            self.select_json_state_form_setting
        )
        state_form_settings_menu.addAction(self.json_form_setting_select)

        settings_menu.addMenu(state_form_settings_menu)

        toolbar.addAction(file_menu.menuAction())
        toolbar.addAction(settings_menu.menuAction())

    def select_basic_state_form_setting(self):
        self.states_form.setting = "basic"
        if self.json_form_setting_select.isChecked():
            self.json_form_setting_select.setChecked(False)

    def select_json_state_form_setting(self):
        self.states_form.setting = "json"
        if self.basic_action.isChecked():
            self.basic_action.setChecked(False)

    def export_file(self):
        """Exports current state as a .json to local storage"""

        scene = self.states_form.scene
        if not scene.items():
            utils.send_error(
                "Export Error", "Workflow is empty. Add a workflow to export"
            )
            return

        fp, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)"
        )

        if fp:
            try:
                workflow = self.states_form.get_workflow(reformat=False)
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(self.create_json(workflow), f, indent=4)
            except Exception:
                print("error")

    def export_as_png(self):
        """Exports current state as a .png to local storage"""

        scene = self.states_form.scene
        if not scene.items():
            utils.send_error(
                "Export Error", "Workflow is empty. Add a workflow to export"
            )
            return

        fp, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")

        if fp:
            pixmap = QPixmap(scene.sceneRect().size().toSize())
            pixmap.fill(QColor(255, 255, 255))
            painter = QPainter(pixmap)
            scene.render(painter, QRectF(pixmap.rect()), scene.sceneRect())
            painter.end()
            pixmap.save(fp, "PNG")

    def import_file(self):
        """Imports a .json file to use a state and loads file into the GUI"""

        # Check if any of the forms contain data before resetting GUI state
        need_to_reset = False
        if self.contains_data():
            if not (
                # set need_to_reset to client's response in the 'Are you sure' popup
                need_to_reset := utils.send_are_you_sure(
                    "This will delete all data in your current workflow."
                )
                == QMessageBox.StandardButton.Yes
            ):
                return

        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Select a JSON File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            # clear forms if state already exists in the GUI
            if need_to_reset:
                self.clear()
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
                    self.states_form.get_workflow(reformat=True)
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
        states = self.states_form.get_workflow(reformat=False)
        json_data = self.create_json(states)

        popup = SubmissionDialog()

        # make worker a GUI attribute to not block the rest of the application
        self.worker = Worker(json_data)
        self.worker.update_text.connect(popup.update_text)

        self.worker.start()
        popup.exec()

    def validate_form(self):
        """Workflow for validating the state. Triggered on the click of the Validate button. Enables the submit
        button if the workflow is validated.
        """
        workflow_path = self.states_form.get_workflow(reformat=False)
        json_data = self.create_json(workflow_path)

        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=ResourceWarning)

        validate_wf = Workflow(json_data)
        valid = validate_wf.validate(verbose=True)
        if valid:
            self.valid_workflow = json_data
            self.submit_button.setEnabled(True)

    def contains_data(self):
        """Check if any forms contain data"""
        return any(
            form.contains_data()
            for form in [self.states_form, self.meta_form, self.import_form]
        )

    def clear(self):
        """Clear all forms"""
        self.meta_form.clear()
        self.import_form.clear()
        self.states_form.clear()
