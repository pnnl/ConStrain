from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QGraphicsView,
    QGraphicsTextItem,
    QGraphicsRectItem,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import (
    QPainter,
    QWheelEvent,
    QKeyEvent,
    QKeySequence,
    QColor,
    QPen,
    QBrush,
)
from constrain.app.popup_window import PopupWindow
from constrain.app.advanced_popup import AdvancedPopup
from constrain.app.rect_connect import Scene, CustomItem, ControlPoint, Path
import json


class Zoom(QGraphicsView):
    clicked = pyqtSignal()

    def __init__(self, scene):
        """QGraphicsView that includes zoom function

        scene (Scene): scene to be contained by self
        """
        super().__init__(scene)
        self.scene = scene
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setOptimizationFlag(
            QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing
        )

        # factor for how much to zoom
        self.zoom = 1.1
        self.zoom_in = QKeySequence.StandardKey.ZoomIn
        self.zoom_out = QKeySequence.StandardKey.ZoomOut

        # last CustomItem that was clicked
        self.itemClicked = None

        # on mouse click + drag, where the drag started
        self.dragStartPosition = None

        # area of selection
        self.selection_rect = None

        self.max_x = 0

    def wheelEvent(self, event: QWheelEvent):
        """Zooms in or out on view"""
        factor = self.zoom ** (event.angleDelta().y() / 240.0)
        self.scale(factor, factor)

    def keyPressEvent(self, event: QKeyEvent):
        """Zooms in or out on view with trackpad event"""
        if event.matches(self.zoom_in):
            self.scale(self.zoom, self.zoom)
            event.accept()
        elif event.matches(self.zoom_out):
            self.scale(1 / self.zoom, 1 / self.zoom)
            event.accept()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        item = self.itemAt(event.pos())
        if item:
            if isinstance(item, QGraphicsTextItem):
                item = item.parentItem()
            elif isinstance(item, ControlPoint):
                return

            if isinstance(item, CustomItem):
                self.itemClicked = item

    def mousePressEvent(self, event):
        """Performs default action then stores clicked item if item is associated with CustomItem"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.itemClicked = None
            self.dragStartPosition = self.mapToScene(event.pos())
            if not self.itemAt(event.pos()):
                self.selection_rect = QGraphicsRectItem()
                pen = QPen(QColor(0, 0, 255))

                pen.setWidth(1)
                self.selection_rect.setPen(pen)
                brush = QBrush(QColor(0, 0, 230))
                color = QColor(0, 0, 255)
                color.setAlphaF(0.2)
                brush = QBrush(color)
                self.selection_rect.setBrush(brush)
                self.scene.addItem(self.selection_rect)

    def mouseMoveEvent(self, event):
        if self.dragStartPosition and self.selection_rect:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self.dragStartPosition, current_pos).normalized()
            self.selection_rect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Performs default action and triggers self.clicked if user action was a click"""
        super().mouseReleaseEvent(event)

        # check if left mouse button release and if item was not dragged
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.mapToScene(event.pos()) == self.dragStartPosition
        ):
            if self.selection_rect:
                self.scene.removeItem(self.selection_rect)
                self.selection_rect = None
                self.dragStartPosition = None
                self.scene.update()

            item = self.itemAt(event.pos())
            if item:
                if isinstance(item, QGraphicsTextItem):
                    item = item.parentItem()
                elif isinstance(item, ControlPoint):
                    return
                if isinstance(item, CustomItem):
                    self.clicked.emit()
                    self.itemClicked = item
        elif self.selection_rect:
            selected_items = []
            rect = self.selection_rect.rect()

            for item in self.scene.items():
                if isinstance(item, CustomItem) and rect.intersects(
                    item.mapRectToScene(item.rect)
                ):
                    print(item.state["Title"])
                    selected_items.append(item)
                    item.setSelected(True)

            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
            self.dragStartPosition = None

            self.scene.update()

    def arrange_tree(self, parent_item, x, y, step):
        """Arranges workflow diagram to form a tree

        Args:
            parent_item (CustomItem): node with children items
            x (float): x value of CustomItem
            y (float): y value of CustomItem
            step (int): spacing factor
        """
        if not parent_item:
            return

        parent_item.setPos(x, y)
        parent_item_h = parent_item.boundingRect().height()
        num_children = len(parent_item.children)
        if num_children:
            total_width = (num_children - 1) * step
            start_x = x - total_width / 2

            for child in parent_item.children:
                self.arrange_tree(child, start_x, y + parent_item_h + 20, step)
                start_x += step


class WorkflowDiagram(QWidget):
    def __init__(self, setting):
        """Widget to contain view

        setting (str): either "basic" or "advanced". Determines if clicking on a CustomItem should bring up a basic form or an advanced form
        """
        super().__init__()

        self.setting = setting
        layout = QVBoxLayout(self)
        self.scene = Scene()
        self.view = Zoom(self.scene)
        self.view.clicked.connect(self.item_clicked)

        # last popup accessed
        self.popup = None

        # buttons
        add_buttons = QHBoxLayout()
        reformat_button_layout = QHBoxLayout()

        basic_button = QPushButton("Add Basic")
        basic_button.setToolTip("Create a state using the basic popup")
        basic_button.setFixedSize(100, 23)
        basic_button.clicked.connect(self.call_popup)
        add_buttons.addWidget(basic_button)

        advanced_button = QPushButton("Add Advanced")
        advanced_button.setToolTip("Create a state using the advanced popup")
        advanced_button.setFixedSize(100, 23)
        advanced_button.clicked.connect(self.call_advanced_popup)
        add_buttons.addWidget(advanced_button)

        reformat_button = QPushButton("Rearrange")
        reformat_button.setToolTip("Rearrange diagram to a tree layout")
        reformat_button.setFixedSize(100, 23)
        reformat_button.clicked.connect(self.get_workflow)
        reformat_button_layout.addWidget(reformat_button)

        add_buttons.setAlignment(Qt.AlignmentFlag.AlignLeft)
        reformat_button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        buttons = QHBoxLayout()
        buttons.addLayout(add_buttons)
        buttons.addLayout(reformat_button_layout)

        layout.addWidget(self.view)
        layout.addLayout(buttons)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

    def add_state(self):
        """Creates CustomItem based on state described in self.popup if there was no error"""
        if self.popup.error:
            return

        state = self.popup.get_state()
        if not state or (state.get("Type", 0) not in ["Choice", "MethodCall"]):
            return

        self.create_item(state)

    def create_item(self, state):
        """Creates and displays a CustomItem which represents the given state

        Args:
            state (dict): state to be made into a CustomItem
        """

        # test whether state was made with popup, or if it was imported. Adds self.popup to CustomItem if not imported
        if (
            self.popup
            and self.popup.get_state()
            and self.popup.get_state()["Title"] == state["Title"]
        ):
            rect_item = CustomItem(state, popup=self.popup)
        else:
            rect_item = CustomItem(state)

        def connect_rects(parent, child):
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
        rects = [item for item in self.scene.items() if isinstance(item, CustomItem)]

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
        self.update()

    def edit_state(self, rect):
        """Gives previously made CustomItem a new state

        Args:
            rect (CustomItem): CustomItem to be edited
        """

        # do not continue if there was an error in self.popup
        if self.popup.error:
            return

        current_state = self.popup.get_state()

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

    def get_workflow(self):
        """Computes structure of the workflow using Depth First Search and paints CustomItems depending on place in graph"""
        items = [item for item in self.scene.items() if isinstance(item, CustomItem)]
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
            self.view.arrange_tree(root, 0, 0, 150)
            if root not in visited:
                dfs_helper(root, [])
            root.setBrush("green")

    def call_popup(self, rect=None, edit=False):
        """Calls popup on click of CustomItem, or if 'Add Basic' button is pressed

        Args:
            rect (CustomItem): CustomItem associated with the popup needed
            edit (bool): False if creating new CustomItem, True otherwise
        """
        payloads = self.scene.getObjectsCreated()
        if rect:
            if not rect.popup or isinstance(rect.popup, AdvancedPopup):
                # make a new popup
                rect.popup = PopupWindow(
                    payloads,
                    state_names=self.scene.getStateNames(),
                    rect=rect,
                    load=True,
                )
            rect.popup.edit_mode(payloads)
            self.popup = rect.popup
        else:
            self.popup = PopupWindow(payloads, state_names=self.scene.getStateNames())

        if edit and rect:
            try:
                self.popup.save_button.clicked.disconnect(self.add_state)
            except TypeError:
                self.popup.save_button.clicked.connect(lambda: self.edit_state(rect))
        else:
            self.popup.save_button.clicked.connect(self.add_state)
        self.popup.exec()

    def call_advanced_popup(self, rect=None, edit=False):
        """Calls popup on click of CustomItem, or if 'Add Advanced' button is pressed"""
        # create new popup
        self.popup = AdvancedPopup(rect, edit)

        if edit and rect:
            try:
                self.popup.save_button.clicked.disconnect(self.add_state)
            except TypeError:
                self.popup.save_button.clicked.connect(lambda: self.edit_state(rect))
        else:
            self.popup.save_button.clicked.connect(self.add_state)
        self.popup.exec()

    def item_clicked(self):
        """When a CustomItem is clicked, calls self.call_popup in order to display popup associated with the CustomItem clicked"""
        if self.view.itemClicked:
            rect = self.view.itemClicked
            if self.setting == "basic":
                self.call_popup(rect, True)
            elif self.setting == "advanced":
                self.call_advanced_popup(rect, True)

    def read_import(self, states):
        """Adds imported states to workflow diagram

        states (dict): states to import
        """
        if isinstance(states, dict):
            for state_name in states.keys():
                # turn state into a dictionary containing state_name key
                new_state = states[state_name]
                new_state["Title"] = state_name
                self.create_item(new_state)

    def contains_data(self):
        """Check if workflow diagram contains any data"""
        return bool(self.scene.items())

    def clear(self):
        """Clear all state"""
        self.scene.clear()
        self.view.resetTransform()
        self.update()
