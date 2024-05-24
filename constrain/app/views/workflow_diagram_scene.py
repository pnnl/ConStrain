from typing import Optional

from PyQt6 import QtCore, QtGui, QtWidgets

from constrain.app.controllers.rect_connect import ControlPoint, Path, CustomItem


class WorkflowDiagramScene(QtWidgets.QGraphicsScene):
    """Scene to display workflow diagram"""

    startItem = newConnection = None

    def controlPointAt(self, pos: QtCore.QPointF) -> Optional[ControlPoint]:
        """Returns ControlPoint at given position

        Args:
            pos (PyQt6.QtCore.QPointF): position
        """

        mask = QtGui.QPainterPath()
        mask.setFillRule(QtCore.Qt.FillRule.WindingFill)
        for item in self.items(pos):
            if mask.contains(pos):
                # ignore objects hidden by others
                return
            if isinstance(item, ControlPoint):
                return item
            if not isinstance(item, Path):
                mask.addPath(item.shape().translated(item.scenePos()))

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """Tries drawing a path on mouse press, otherwise default action"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # check if mouse press at ControlPoint object
            item = self.controlPointAt(event.scenePos())
            if item:
                # start a path
                self.startItem = item
                self.newConnection = Path(item, event.scenePos())
                self.addItem(self.newConnection)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """Tries tracing path from starting ControlPoint to next ControlPoint, otherwise default action"""
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and item != self.startItem:
                p2 = item.scenePos()
            else:
                p2 = event.scenePos()
            self.newConnection.setP2(p2)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """Tries connecting start ControlPoint to end ControlPoint, otherwise default action"""
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and item != self.startItem:
                self.newConnection.setEnd(item)
                if self.startItem.addLine(self.newConnection):
                    item.addLine(self.newConnection)
                else:
                    # delete the connection if it exists; remove the following line if this feature is not required
                    self.startItem.removeLine(self.newConnection)
                    self.removeItem(self.newConnection)
            else:
                self.removeItem(self.newConnection)
        self.startItem = self.newConnection = None
        super().mouseReleaseEvent(event)

    def getObjectsinUse(self) -> list:
        """Returns objects that are used in this scene

        Returns:
            list: list of object names that are used in this scene
        """
        rect_items = [item for item in self.items() if isinstance(item, CustomItem)]
        objects_in_use = []
        for rect_item in rect_items:
            rect_item_objects = rect_item.get_objects_used()
            for rect_item_object in rect_item_objects:
                objects_in_use.append(rect_item_object)
        return objects_in_use

    def getObjectsCreated(self) -> list:
        """Returns objects that are created in this scene

        Returns:
            list: list of object names that are created in this scene
        """
        rect_items = [item for item in self.items() if isinstance(item, CustomItem)]
        objects_in_use = []
        for rect_item in rect_items:
            rect_item_objects = rect_item.get_objects_created()
            for rect_item_object in rect_item_objects:
                objects_in_use.append(rect_item_object)
        return objects_in_use

    def getStateNames(self) -> list:
        """Returns state names that are created in this scene

        Returns:
            list: list of state names that have been created
        """
        rect_items = [item for item in self.items() if isinstance(item, CustomItem)]
        state_names = []
        for rect_item in rect_items:
            rect_name = rect_item.state["Title"]
            state_names.append(rect_name)
        return state_names
