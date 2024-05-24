import json
from typing import Optional

from PyQt6 import QtWidgets, QtCore

from constrain.app.views.basic_state_form import BasicStateForm
from constrain.app.views.json_state_form import JSONStateForm
from constrain.app.views.workflow_diagram_scene import WorkflowDiagramScene
from constrain.app.views.workflow_diagram_view import ZoomView
from constrain.app.controllers.rect_connect import CustomItem, Path
from constrain.app.utils import utils


class WorkflowDiagram(QtWidgets.QWidget):
    def __init__(self, setting: str) -> None:
        """Widget to contain view

        setting (str): either "basic" or "json". Determines if clicking on a CustomItem should bring up a basic form or an json form
        """
        super().__init__()

        self.setting = setting
        layout = QtWidgets.QVBoxLayout(self)
        self.scene = WorkflowDiagramScene()
        self.view = ZoomView(self.scene)
        self.view.clicked.connect(self.item_clicked)

        # last state form accessed
        self.last_state_form = None

        self.root = None

        # buttons
        add_buttons = QtWidgets.QHBoxLayout()
        reformat_button_layout = QtWidgets.QHBoxLayout()

        add_state_button = QtWidgets.QPushButton("Add State")
        add_state_button.setToolTip("Create a state using the basic form")
        add_state_button.setFixedSize(100, 23)
        add_state_button.clicked.connect(self.display_state_form)
        add_buttons.addWidget(add_state_button)

        reformat_button = QtWidgets.QPushButton("Rearrange")
        reformat_button.setToolTip("Rearrange diagram to a tree layout")
        reformat_button.setFixedSize(100, 23)
        reformat_button.clicked.connect(self.get_workflow)
        reformat_button_layout.addWidget(reformat_button)

        add_buttons.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        reformat_button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addLayout(add_buttons)
        buttons.addLayout(reformat_button_layout)

        layout.addWidget(self.view)
        layout.addLayout(buttons)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

    def display_state_form(self) -> None:
        if self.setting == "basic":
            self.display_basic_state_form()
        else:
            self.display_json_state_form()

    def add_state(self) -> None:
        """Creates CustomItem based on state described in self.last_state_form if there was no error"""
        if self.last_state_form.error:
            return

        state = self.last_state_form.get_state()
        self.create_item(state)

    def create_item(self, state: dict) -> None:
        """Creates and displays a CustomItem which represents the given state

        Args:
            state (dict): state to be made into a CustomItem
        """

        # test whether state was made with state form or if it was imported. Adds self.last_state_form to CustomItem if not imported
        if self.last_state_form and self.last_state_form.get_state():
            self.last_state_form.get_state()["Title"]

        if self.last_state_form and self.last_state_form.get_state():
            state["Title"]

        if (
            self.last_state_form
            and self.last_state_form.get_state()
            and self.last_state_form.get_state()["Title"] == state["Title"]
        ):
            state_form_used = True
            rect_item = CustomItem(state, last_state_form=self.last_state_form)
        else:
            state_form_used = False
            rect_item = CustomItem(state)

        rect_item.deleted.connect(self.delete_state)
        rect_item.edited.connect(self.display_edit_state_form)

        def connect_rects(parent: CustomItem, child: CustomItem):
            """Connects a parent CustomItem to a child CustomItem

            Args:
                parent (CustomItem): parent CustomItem
                child (CustomItem): child CustomItem
            """
            child_control = child.controls[2]
            parent_control = parent.controls[0]
            path = Path(parent_control, child_control.scenePos(), child_control)
            if parent_control.addLine(path) and child_control.addLine(path):
                self.scene.addItem(path)

        # find CustomItems in scene
        rects = self.get_rects_in_scene()

        if state.get("End"):
            if self.is_new_end_state_valid(rect_item):
                rect_item.setBrush("red")
            else:
                utils.send_error(
                    "Error in Workflow", "This item cannot be an end state"
                )
                return
        elif state.get("Start"):
            if self.is_new_start_state_valid(rect_item):
                rect_item.setBrush("green")
            else:
                utils.send_error(
                    "Error in Workflow", "This item cannot be a start state"
                )
                return

        # if parent and child exist in the scene, connect them with a Path
        if "Next" in state.keys():
            matching_rects = [
                rect for rect in rects if rect.state["Title"] == state["Next"]
            ]
            if len(matching_rects) == 1:
                child_rect = matching_rects[0]
                connect_rects(rect_item, child_rect)

        for rect in rects:
            nexts = rect.get_nexts()
            for next in nexts:
                if next == state["Title"]:
                    connect_rects(rect, rect_item)

        self.scene.addItem(rect_item)

        if rects:
            stepsize = 20
            rect_with_max_y = None
            max_y = 0
            for rect in rects:
                if rect.y() >= max_y:
                    max_y = rect.y()
                    rect_with_max_y = rect
            size = rect_with_max_y.boundingRect().height()
            rect_item.setPos(0, max_y + size + stepsize)

        if state_form_used:
            self.last_state_form.close()

        self.update()

    def delete_state(self, obj: CustomItem) -> None:
        objects_created = obj.get_objects_created()
        all_objects_in_use = self.scene.getObjectsinUse()
        for created_object in objects_created:
            if created_object in all_objects_in_use:
                utils.send_error("Error in State", "Object created in use")
                return

        # remove lines
        for c in obj.controls:
            for p in c.paths:
                p1 = p.start
                p2 = p.end
                if p1 in obj.controls:
                    p2.removeLine(p)
                else:
                    p1.removeLine(p)

        self.scene.removeItem(obj)

    def is_new_start_state_valid(self, rect: CustomItem) -> bool:
        rects = self.get_rects_in_scene()
        start_or_end_state_rects = [
            rect
            for rect in rects
            if rect.state.get("Start") and rect.state["Start"] == "True"
        ]

        rect_has_no_parents = not any(
            rect in possible_parents.children for possible_parents in rects
        )
        return len(start_or_end_state_rects) == 0 and rect_has_no_parents

    def get_rect_parents(self, rect: CustomItem) -> list:
        return [
            parent for parent in self.get_rects_in_scene() if rect in parent.children
        ]

    def is_new_end_state_valid(self, rect: CustomItem) -> bool:
        return len(rect.children) == 0

    def get_rects_in_scene(self) -> list:
        return [item for item in self.scene.items() if isinstance(item, CustomItem)]

    def edit_state(self, rect: CustomItem) -> None:
        """Gives previously made CustomItem a new state

        Args:
            rect (CustomItem): CustomItem to be edited
        """

        # do not continue if there was an error in self.last_state_form
        if self.last_state_form.error:
            return

        current_state = self.last_state_form.get_state()

        if current_state["Type"] not in ["Choice", "MethodCall"]:
            return

        # give CustomItem new state
        old_state = rect.get_state_string()
        old_state = json.loads(old_state)
        title = next(iter(old_state.keys()))
        old_state = old_state[title]
        old_state["Title"] = title

        if old_state != current_state:
            rect.set_state(current_state)

        if current_state.get("End"):
            if self.is_new_end_state_valid(rect):
                rect.setBrush("red")
            else:
                utils.send_error(
                    "Error in Workflow", "This item cannot be an end state"
                )
                return
        elif current_state.get("Start"):
            if self.is_new_start_state_valid(rect):
                rect.setBrush("green")
            else:
                utils.send_error(
                    "Error in Workflow", "This item cannot be a start state"
                )
                return

        self.last_state_form.close()

    def get_workflow(self, reformat: bool = True) -> Optional[list]:
        """Computes structure of the workflow using Depth First Search and paints CustomItems depending on place in graph"""
        if not reformat:
            reformat = True

        items = self.get_rects_in_scene()

        roots = []
        for i in items:
            parent = True
            for j in items:
                if i in j.children:
                    parent = False
                    break
            if parent:
                roots.append(i)

        if len(roots) == 0:
            return
        elif len(roots) > 1:
            utils.send_error("Error in Workflow", "More than 1 root node")
            return
        else:
            root = roots[0]

        visited1 = set()
        paths = []

        def dfs_helper(item, path: list) -> None:
            path.append(item)
            visited1.add(item)

            if item not in items or not item.children:
                # item is a leaf node
                item.setBrush("red")
                item.state["End"] = "True"
                item.state.pop("Next", None)
                paths.append(path[:])
            else:
                # item is not a leaf node
                item.setBrush()

            for child in item.children:
                if child not in visited1:
                    dfs_helper(child, path)

            path.pop()
            visited1.remove(item)

        if reformat:
            self.view.arrange_tree(root, 0, 0, 150)
        if root not in visited1:
            dfs_helper(root, [])

        self.root = root
        root.state["Start"] = "True"
        root.setBrush("green")

        visited2 = set()
        workflow_path = []
        for path in paths:
            for node in path:
                if node not in visited2:
                    workflow_path.append(node.state)
                    visited2.add(node)
        return workflow_path

    def display_basic_state_form(
        self, rect: CustomItem = None, edit: bool = False
    ) -> None:
        """Displays basic state form on click of CustomItem, or if 'Add Basic' button is pressed

        Args:
            rect (CustomItem): CustomItem associated with the state form needed
            edit (bool): False if creating new CustomItem, True otherwise
        """
        payloads = self.scene.getObjectsCreated()
        if rect:
            if not rect.state_form or isinstance(rect.state_form, JSONStateForm):
                # make a new state form
                rect.state_form = BasicStateForm(
                    payloads,
                    state_names=self.scene.getStateNames(),
                    rect=rect,
                    load=True,
                )
            rect.state_form.edit_mode(payloads)
            self.last_state_form = rect.state_form
        else:
            self.last_state_form = BasicStateForm(
                payloads, state_names=self.scene.getStateNames()
            )

        if edit and rect:
            try:
                self.last_state_form.save_button.clicked.disconnect(self.add_state)
            except TypeError:
                self.last_state_form.save_button.clicked.connect(
                    lambda: self.edit_state(rect)
                )
        else:
            self.last_state_form.save_button.clicked.connect(self.add_state)
        self.last_state_form.exec()

    def display_json_state_form(
        self, rect: CustomItem = None, edit: bool = False
    ) -> None:
        """Calls state form on click of CustomItem, or if 'Add' button is pressed with JSON state form setting selected"""
        # create new state form
        self.last_state_form = JSONStateForm(rect, edit)

        if edit and rect:
            try:
                self.last_state_form.save_button.clicked.disconnect(self.add_state)
            except TypeError:
                self.last_state_form.save_button.clicked.connect(
                    lambda: self.edit_state(rect)
                )
        else:
            self.last_state_form.save_button.clicked.connect(self.add_state)
        self.last_state_form.exec()

    def item_clicked(self) -> None:
        """When a CustomItem is clicked, calls self.display_edit_state_form in order to display state form associated with the CustomItem clicked"""
        if self.view.itemClicked:
            rect = self.view.itemClicked
            if isinstance(rect, CustomItem):
                self.display_edit_state_form(rect)

    def display_edit_state_form(self, rect: CustomItem) -> None:
        if self.setting == "basic":
            self.display_basic_state_form(rect, True)
        else:
            self.display_json_state_form(rect, True)

    def read_import(self, states: dict) -> None:
        """Adds imported states to workflow diagram

        states (dict): states to import
        """
        if isinstance(states, dict):
            for state_name in states.keys():
                # turn state into a dictionary containing state_name key
                new_state = states[state_name]
                new_state["Title"] = state_name
                self.create_item(new_state)

    def contains_data(self) -> bool:
        """Check if workflow diagram contains any data"""
        return bool(self.scene.items())

    def clear(self) -> None:
        """Clear all state"""
        self.scene.clear()
        self.last_state_form = None
        self.root = None
        self.view.resetTransform()
        self.update()
