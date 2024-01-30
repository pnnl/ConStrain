"""
This file contains the classes Path, ControlPoint, CustomItem, and Scene. These classes form the visual aspect of the States tab in the GUI.
CustomItem contains the state, Path links 2 ControlPoints with an arrowed line, ControlPoints are on the edges of CustomItems, and Scene contains
all of this.
"""
import json
import math
import re

from PyQt6 import QtCore, QtGui, QtWidgets

from . import utils


class Path(QtWidgets.QGraphicsPathItem):
    def __init__(self, start, p2, end=None):
        """Initializes a Path from start to p2

        Args:
            start (ControlPoint): where the path starts
            p2 (PyQt6.QtCore.QPointF): where the path currently is
            end (ControlPoint): where the path ends
        """
        super(Path, self).__init__()

        self.start = start
        self.end = end

        # set arrow shape
        self._arrow_height = 5
        self._arrow_width = 4

        # create QPainterPath from start's position to p2 and set this as the path
        self._path = QtGui.QPainterPath()
        self._path.moveTo(start.scenePos())
        self._path.lineTo(p2)

        self.setPath(self._path)

    def controlPoints(self):
        """Returns control points that this path connects

        Returns:
            ControlPoint: start control point
            ControlPoint: end control point
        """
        return self.start, self.end

    def setP2(self, p2):
        """Sets path to given point

        Args:
            p2 (PyQt6.QtCore.QPointF): where the path needs to be
        """
        self._path.lineTo(p2)
        self.setPath(self._path)

    def setStart(self, start):
        """Sets start

        Args:
            start (ControlPoint): new start
        """
        self._start = start
        self.updatePath()

    def setEnd(self, end):
        """Sets end

        Args:
            end (ControlPoint): new end
        """
        self.end = end
        self.updatePath(end)

    def updatePath(self, source):
        """Updates path from start to end

        source (ControlPoint): where the path starts
        """
        if source == self.start:
            self._path = QtGui.QPainterPath(source.scenePos())
            self._path.lineTo(self.end.scenePos())
        else:
            self._path = QtGui.QPainterPath(self.start.scenePos())
            self._path.lineTo(source.scenePos())

        self.setPath(self._path)

    def arrowCalc(self, start_point=None, end_point=None):
        """Calculates the point where the arrow should be drawn

        Args:
            start_point (ControlPoint): start control point
            end_point (ControlPoint): end control point

        Returns:
            PyQt6.QtGui.QPolygonF: arrow, None if invalid
        """
        try:
            # set start and end
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self.start

            if endPoint is None:
                endPoint = self.end

            # find distance between start and end
            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx**2 + dy**2)

            # normalize
            normX, normY = dx / leng, dy / leng

            # perpendicular vector
            perpX = -normY
            perpY = normX

            # define position of arrows
            leftX = (
                endPoint.x() + self._arrow_height * normX + self._arrow_width * perpX
            )
            leftY = (
                endPoint.y() + self._arrow_height * normY + self._arrow_width * perpY
            )

            rightX = (
                endPoint.x() + self._arrow_height * normX - self._arrow_width * perpX
            )
            rightY = (
                endPoint.y() + self._arrow_height * normY - self._arrow_width * perpY
            )

            point2 = QtCore.QPointF(leftX, leftY)
            point3 = QtCore.QPointF(rightX, rightY)

            return QtGui.QPolygonF([point2, endPoint, point3])

        # leng == 0 or something else
        except (ZeroDivisionError, Exception):
            return None

    def directPath(self):
        """Returns a direct path from start ControlPoint to end ControlPoint"""
        path = QtGui.QPainterPath(self.start.scenePos())
        path.lineTo(self.end.scenePos())
        return path

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        """Paints path"""
        painter.pen().setWidth(2)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        # define direct path and arrow if end is defined
        if self.end:
            path = self.directPath()
            triangle_source = self.arrowCalc(
                path.pointAtPercent(0.1), self.end.scenePos()
            )
        else:
            path = self._path
            triangle_source = None
        painter.drawPath(path)
        self.setPath(path)

        # draw arrow
        if triangle_source is not None:
            painter.drawPolyline(triangle_source)

    def contextMenuEvent(self, event):
        """Context menu for deletion on path

        Args:
            event (PyQt6.QtWidgets.QGraphicsSceneContextMenuEvent): right click event
        """
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec(event.screenPos())

        # removeLine from start ControlPoint and end ControlPoint
        if action == delete_action:
            self.start.removeLine(self)
            self.end.removeLine(self)


class ControlPoint(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent):
        """QGraphicsEllipseItem to act as point on edge of CustomItem and endpoint of Path

        Args:
            parent (CustomItem): CustomItem that ControlPoint belongs to
        """
        super().__init__(-5, -5, 10, 10, parent)
        self.parent = parent

        # list of Path objects that include this control point
        self.paths = []

        self.setAcceptHoverEvents(True)
        self.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges
        )

        self.setOpacity(0.3)

        # whether or not this ControlPoint has been clicked
        # TODO Find out if I need this
        self.clicked = False

    def addLine(self, pathItem):
        """Adds path to self if the path is viable

        Args:
            pathItem (Path): Path to connect to self

        Returns:
            bool: True if path is viable, False otherwise
        """

        # determine whether path is viable
        viable = self.newLineErrorCheck(pathItem)

        if viable:
            self.paths.append(pathItem)
            return True
        return False

    def newLineErrorCheck(self, pathItem):
        """Checks pathItem to determine whether it is a viable path

        Args:
            pathItem (Path): path in question

        Returns:
            bool: True if pathItem is viable, False otherwise
        """

        # return False if path already exists
        for existing in self.paths:
            if existing.controlPoints() == pathItem.controlPoints():
                return False

        # only consider sending error message if self is the start of the path
        if pathItem.start == self:
            # determine if parent will have too many children states
            rect_children_amt = len(self.parent.children)
            if rect_children_amt >= 1:
                if self.parent.state["Type"] != "Choice":
                    # MethodCall type CustomItem can only connect to 1 CustomItem
                    utils.send_error(
                        "Error in Path", "This type cannot connect to more than 1 state"
                    )
                    return False
                elif self.parent.state["Type"] == "Choice":
                    # Choice type CustomItem can connect to more than 1 CustomItem, but need to see how many are defined in the state
                    choices_amt = len(self.parent.state["Choices"])
                    if "Default" in self.parent.state.keys():
                        choices_amt += 1

                    if rect_children_amt >= choices_amt:
                        error_msg = f"This type cannot connect to more than {choices_amt} states"
                        utils.send_error("Error in Path", error_msg)
                        return False
            # add new child node to parent.children since path is viable
            self.parent.children.append(pathItem.end.parent)
        return True

    def removeLine(self, pathItem):
        """Given pathItem to remove, removes pathItem from scene and self.paths

        Args:
            pathItem (Path): pathItem to remove

        Returns:
            bool: True if pathItem was removed from ControlPoint, False otherwise
        """
        for existing in self.paths:
            # find matching path in existing
            if existing.controlPoints() == pathItem.controlPoints():
                self.scene().removeItem(existing)
                self.paths.remove(existing)

                # remove child node from parent CustomItem since they are no longer connected
                if pathItem.start == self:
                    self.parent.children.remove(pathItem.end.parent)
                return True
        return False

    def itemChange(self, change, value):
        """Updates path on item change for path in paths"""
        for path in self.paths:
            path.updatePath(self)
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        """Change opacity when hovered over"""
        self.setOpacity(1.0)

    def hoverLeaveEvent(self, event):
        """Change opacity when not hovered over"""
        self.setOpacity(0.3)


class CustomItem(QtWidgets.QGraphicsItem):
    # ControlPoint outline
    controlBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))

    def __init__(self, state, popup=None):
        """Shape on Scene to represents a state in the workflow

        Args:
            state (dict): state that self represents
            popup (PopupWindow or AdvancedPopup): popup associated with self
        """
        super().__init__()
        # fill
        self.pen = QtGui.QPen(QtGui.QColor(98, 99, 102, 255))
        self.brush = QtGui.QBrush(QtGui.QColor(214, 127, 46))
        self.state = state
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.rect = QtCore.QRectF(0, 0, 100, 30)
        self.titleItem = QtWidgets.QGraphicsTextItem(parent=self)

        self.popup = popup

        # child states (list of CustomItems)
        self.children = []

        # ControlPoints on self
        self.controls = []
        self.initialize_ui()

    def initialize_ui(self):
        """Initialize how self looks"""

        if "Title" not in self.state.keys():
            self.state["Title"] = ""
        title = self.state["Title"]

        # display title on self
        self.titleItem.setHtml(f"<center>{title}</center>")

        max_width = 100
        self.titleItem.setTextWidth(max_width)

        self.titleRect = self.titleItem.boundingRect()
        text_width = self.titleRect.width()
        text_height = self.titleRect.height()

        # make width and height of shape a bit larger than text
        w = text_width * 1.2
        h = text_height * 1.2

        self.rect.setRect(0, 0, w, h)

        self.titleRect.moveCenter(self.rect.center())
        self.titleItem.setPos(self.titleRect.topLeft())

        # where to place control points
        control_placements = [
            (self.rect.width() / 2, self.rect.height()),
            (self.rect.width(), self.rect.height() / 2),
            (self.rect.width() / 2, 0),
            (0, self.rect.height() / 2),
        ]

        # initialize control points
        if not self.controls:
            self.controls = [ControlPoint(self) for i in range(len(control_placements))]

        # draw control points
        for i, control in enumerate(self.controls):
            control.setPen(self.pen)
            control.setBrush(self.controlBrush)
            control.setX(control_placements[i][0])
            control.setY(control_placements[i][1])

    def boundingRect(self):
        """Make bounding rect a little larger so that it is easier to click"""
        adjust = self.pen.width() / 2
        return self.rect.adjusted(-adjust, -adjust, adjust, adjust)

    def paint(self, painter, option, widget=None):
        """Paints self on scene"""
        painter.save()

        if self.isSelected():
            self.pen.setWidth(2)
        else:
            self.pen.setWidth(1)

        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        if self.state["Type"] == "Choice":
            # make shape a diamond if state is a choice type
            diamond_points = [
                QtCore.QPointF(self.rect.center().x(), self.rect.top()),
                QtCore.QPointF(self.rect.right(), self.rect.center().y()),
                QtCore.QPointF(self.rect.center().x(), self.rect.bottom()),
                QtCore.QPointF(self.rect.left(), self.rect.center().y()),
            ]
            painter.drawPolygon(QtGui.QPolygonF(diamond_points))
        else:
            # else, make it a rounded rectangle
            painter.drawRoundedRect(self.rect, 4, 4)
        painter.restore()

    def setBrush(self, color="orange"):
        """Sets color of fill on self

        Args:
            color (str): color to be changed to; ideally should
            be "red", "green", or "orange"
        """
        if color == "red":
            color = QtGui.QColor(214, 54, 64)
        elif color == "green":
            color = QtGui.QColor(10, 168, 89)
        else:
            color = QtGui.QColor(214, 127, 46)
        self.brush = QtGui.QBrush(color)
        self.update()

    def contextMenuEvent(self, event):
        """Context menu to allow deletion of self in scene"""
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Delete")

        action = menu.exec(event.screenPos())

        if action == delete_action:
            # find payloads that self.state has created
            objects_created = self.get_objects_created()

            # find what objects are currently being used by other states
            all_objects_in_use = self.scene().getObjectsinUse()

            # make sure that payloads from self.state are not being used by another state
            for created_object in objects_created:
                if created_object in all_objects_in_use:
                    self.sendError("Object created in use")
                    return

            # remove lines
            for c in self.controls:
                for p in c.paths:
                    p1 = p.start
                    p2 = p.end
                    if p1 in self.controls:
                        p2.removeLine(p)
                    else:
                        p1.removeLine(p)
            self.scene().removeItem(self)

    def sendError(self, text):
        """Displays an error message given text

        Args:
            text (str): error message to display
        """
        error_msg = QtWidgets.QMessageBox()
        error_msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Error in State")
        error_msg.setText(text)
        error_msg.exec()

    def get_objects_created(self):
        """Returns objects that self.state has created

        Returns:
            list: list of object names (strs)
        """
        if self.state["Type"] == "MethodCall":
            if "Payloads" in self.state:
                payloads = self.state["Payloads"]
                return [object_name for object_name in payloads]
        return []

    def get_objects_used(self):
        """Returns objects that are used from self.state

        Returns:
            list: list of object names that self.state uses
        """
        objects = []
        pattern = r"Payloads\['(.*?)'\]"
        if self.state["Type"] == "MethodCall":
            methodcall = self.state["MethodCall"]
            match = re.search(pattern, methodcall)

            if match:
                object = match.group(1)
                objects.append(object)
        elif self.state["Type"] == "Choice":
            choices = self.state["Choices"]
            for choice in choices:
                match = re.search(pattern, choice["Value"])

                if match:
                    object = match.group(1)
                    objects.append(object)
        return objects

    def get_state_string(self):
        """Returns state in API format

        Returns:
            dict: self.state in API format
        """
        copy_of_state = dict(self.state)

        # make state['Title'] a key for rest of state
        title = copy_of_state.pop("Title")
        state_string = json.dumps({title: copy_of_state}, indent=4)
        return state_string

    def set_state(self, new_state):
        """Given an updated state, updates self

        Args:
            new_state (dict): new state
        """

        self.state = new_state
        self.initialize_ui()

    def get_nexts(self):
        """Returns children names of self

        Returns:
            list: list of children names
        """
        next = []
        if self.state["Type"] == "MethodCall":
            if "Next" in self.state.keys():
                next.append(self.state["Next"])
        else:
            if "Choices" in self.state.keys():
                choices = self.state["Choices"]
                if isinstance(choices, list):
                    next = [
                        choices[i]["Next"]
                        for i in range(len(choices))
                        if "Next" in choices[i]
                    ]
                elif isinstance(choices, dict):
                    if "Next" in choices.keys():
                        next = [choices["Next"]]
            if "Default" in self.state.keys():
                next.append(self.state["Default"])
        return next


class Scene(QtWidgets.QGraphicsScene):
    """Scene to display workflow diagram"""

    startItem = newConnection = None

    def controlPointAt(self, pos):
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

    def mousePressEvent(self, event):
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

    def mouseMoveEvent(self, event):
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

    def mouseReleaseEvent(self, event):
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

    def getObjectsinUse(self):
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

    def getObjectsCreated(self):
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

    def getStateNames(self):
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
