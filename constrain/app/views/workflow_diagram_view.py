from collections import Counter

from PyQt6 import QtWidgets, QtCore, QtGui

from constrain.app.controllers.rect_connect import CustomItem, ControlPoint
from constrain.app.views.workflow_diagram_scene import WorkflowDiagramScene
from constrain.app.utils import utils


class ZoomView(QtWidgets.QGraphicsView):
    clicked = QtCore.pyqtSignal()

    def __init__(self, scene: WorkflowDiagramScene) -> None:
        """QGraphicsView that includes zoom function

        scene (WorkflowDiagramScene): scene to be contained by ZoomView
        """
        super().__init__(scene)
        self.scene = scene
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setOptimizationFlag(
            QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing
        )

        # factor for how much to zoom
        self.zoom = 1.1
        self.zoom_in = QtGui.QKeySequence.StandardKey.ZoomIn
        self.zoom_out = QtGui.QKeySequence.StandardKey.ZoomOut

        # last CustomItem that was clicked
        self.itemClicked = None

        # on mouse click + drag, where the drag started
        self.dragStartPosition = None

        # area of selection
        self.selection_rect = None

        self.max_x = 0

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Zooms in or out on view"""
        factor = self.zoom ** (event.angleDelta().y() / 240.0)
        self.scale(factor, factor)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Zooms in or out on view with trackpad event"""
        if event.matches(self.zoom_in):
            self.scale(self.zoom, self.zoom)
            event.accept()
        elif event.matches(self.zoom_out):
            self.scale(1 / self.zoom, 1 / self.zoom)
            event.accept()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        menu = QtWidgets.QMenu(self)

        # Check if there's an item under the mouse cursor
        selected_states = [
            item
            for item in self.scene.items()
            if item.isSelected() and isinstance(item, CustomItem)
        ]
        if selected_states:
            delete_action = QtGui.QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_items(selected_states))
            menu.addAction(delete_action)
        else:
            item = self.itemAt(event.pos())

            if isinstance(item, CustomItem):
                delete_action = QtGui.QAction("Delete", self)
                delete_action.triggered.connect(item.delete)
                menu.addAction(delete_action)

        menu.exec(event.globalPos())

    def delete_items(self, item_list: list) -> None:
        all_objects_in_use = Counter(self.scene.getObjectsinUse())
        objects_used_in_items = Counter(
            [
                item_object
                for item in item_list
                for item_object in item.get_objects_used()
            ]
        )
        objects_not_used_in_items = set(all_objects_in_use - objects_used_in_items)
        objects_created_in_items = set()
        for item in item_list:
            objects_created_in_items |= set(item.get_objects_created())

        intersection = objects_created_in_items & objects_not_used_in_items
        if intersection:
            error_msg_object = ", ".join(intersection)
            error_msg = f"{error_msg_object} being used by other state"
            if len(intersection) > 1:
                error_msg += "s"
            utils.send_error("Error deleting state", error_msg)
            return

        for item in item_list:
            item.delete()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        item = self.itemAt(event.pos())
        if item:
            if isinstance(item, QtWidgets.QGraphicsTextItem):
                item = item.parentItem()
            elif isinstance(item, ControlPoint):
                return

            if isinstance(item, CustomItem):
                self.itemClicked = item

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Performs default action then stores clicked item if item is associated with CustomItem"""
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.itemClicked = None
            self.dragStartPosition = self.mapToScene(event.pos())
            if not self.itemAt(event.pos()):
                self.selection_rect = QtWidgets.QGraphicsRectItem()
                pen = QtGui.QPen(QtGui.QColor(0, 0, 255))

                pen.setWidth(1)
                self.selection_rect.setPen(pen)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 230))
                color = QtGui.QColor(0, 0, 255)
                color.setAlphaF(0.2)
                brush = QtGui.QBrush(color)
                self.selection_rect.setBrush(brush)
                self.scene.addItem(self.selection_rect)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.dragStartPosition and self.selection_rect:
            current_pos = self.mapToScene(event.pos())
            rect = QtCore.QRectF(self.dragStartPosition, current_pos).normalized()
            self.selection_rect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """Performs default action and triggers self.clicked if user action was a click"""
        super().mouseReleaseEvent(event)

        # check if left mouse button release and if item was not dragged
        if (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self.mapToScene(event.pos()) == self.dragStartPosition
        ):
            if self.selection_rect:
                self.scene.removeItem(self.selection_rect)
                self.selection_rect = None
                self.dragStartPosition = None
                self.scene.update()

            item = self.itemAt(event.pos())
            if item:
                if isinstance(item, QtWidgets.QGraphicsTextItem):
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
                    selected_items.append(item)
                    item.setSelected(True)

            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
            self.dragStartPosition = None

            self.scene.update()

    def arrange_tree(
        self, parent_item: CustomItem, x: float, y: float, step: int
    ) -> None:
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
