from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QGraphicsView,
    QGraphicsTextItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QWheelEvent, QKeyEvent, QKeySequence
from popup_window import PopupWindow
from advanced_popup import AdvancedPopup
from rect_connect import Scene, CustomItem, ControlPoint, Path
import json

with open("dependencies.json") as file:
    data = json.load(file)


class Zoom(QGraphicsView):
    clicked = pyqtSignal()

    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setOptimizationFlag(
            QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing
        )

        self.zoom = 1.1
        self.zoom_in = QKeySequence.StandardKey.ZoomIn
        self.zoom_out = QKeySequence.StandardKey.ZoomOut
        self.itemClicked = None
        self.dragStartPosition = None

    def wheelEvent(self, event: QWheelEvent):
        factor = self.zoom ** (event.angleDelta().y() / 240.0)
        self.scale(factor, factor)

    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(self.zoom_in):
            self.scale(self.zoom, self.zoom)
            event.accept()
        elif event.matches(self.zoom_out):
            self.scale(1 / self.zoom, 1 / self.zoom)
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.pos()
            item = self.itemAt(event.pos())
            if item:
                if isinstance(item, QGraphicsTextItem):
                    item = item.parentItem()
                elif isinstance(item, ControlPoint):
                    return
                if isinstance(item, CustomItem):
                    self.itemClicked = item

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.pos() == self.dragStartPosition
        ):
            item = self.itemAt(event.pos())
            if item:
                if isinstance(item, QGraphicsTextItem):
                    item = item.parentItem()
                elif isinstance(item, ControlPoint):
                    return
                if isinstance(item, CustomItem):
                    self.clicked.emit()
                    self.itemClicked = item

    def arrange_tree(self, parent_item, x, y, step):
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
        super().__init__()

        self.setting = setting
        layout = QVBoxLayout(self)
        self.scene = Scene()
        self.view = Zoom(self.scene)
        self.view.clicked.connect(self.item_clicked)
        self.popup = None

        self.add_button = QPushButton("Add")
        self.add_button.setFixedSize(100, 20)
        self.add_button.clicked.connect(self.call_popup)

        layout.addWidget(self.view)
        layout.addWidget(self.add_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

    def add_state(self):
        if self.popup.error:
            return

        state = self.popup.get_state()
        if "Type" in state.keys() and state["Type"] not in ["Choice", "MethodCall"]:
            return

        self.create_item(state)

    def create_item(self, state):
        if self.popup:
            rect_item = CustomItem(state, left=True, popup=self.popup)
        else:
            rect_item = CustomItem(state, left=True)

        def connect_rects(parent, child):
            child_control = child.controls[2]
            parent_control = parent.controls[0]
            path = Path(parent_control, child_control.scenePos(), child_control)
            if parent_control.addLine(path) and child_control.addLine(path):
                self.scene.addItem(path)

        rects = [item for item in self.scene.items() if isinstance(item, CustomItem)]
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
        self.update()

    def edit_state(self, rect):
        current_state = self.popup.get_state()

        if current_state["Type"] not in ["Choice", "MethodCall"]:
            return

        old_state = rect.get_state_string()
        old_state = json.loads(old_state)
        title = next(iter(old_state.keys()))
        old_state = old_state[title]
        old_state["Title"] = title

        if old_state != current_state:
            rect.set_state(current_state)

    def call_popup(self, rect=None, edit=False):
        if self.setting == "basic":
            payloads = self.scene.getObjectsCreated()
            if rect:
                if not rect.popup:
                    rect.popup = PopupWindow(payloads, rect, load=True)
                rect.popup.edit_mode(payloads, rect, load=True)
                self.popup = rect.popup
            else:
                self.popup = PopupWindow(payloads)
        else:
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
        if self.view.itemClicked:
            rect = self.view.itemClicked
            self.call_popup(rect, True)

    def read_import(self, states):
        if isinstance(states, dict):
            for state_name in states.keys():
                # turn state into a dictionary containing state_name key
                new_state = states[state_name]
                new_state["Title"] = state_name
                self.create_item(new_state)
