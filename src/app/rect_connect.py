from PyQt6 import QtCore, QtGui, QtWidgets
import json
import math
import re


class Path(QtWidgets.QGraphicsPathItem):
    def __init__(self, start, p2, end=None):
        super(Path, self).__init__()

        self.start = start
        self.end = end

        self._arrow_height = 5
        self._arrow_width = 4

        self._path = QtGui.QPainterPath()
        self._path.moveTo(start.scenePos())
        self._path.lineTo(p2)

        self.setPath(self._path)

    def controlPoints(self):
        return self.start, self.end

    def setP2(self, p2):
        self._path.lineTo(p2)
        self.setPath(self._path)

    def setStart(self, start):
        self._start = start
        self.updatePath()

    def setEnd(self, end):
        self.end = end
        self.updatePath(end)

    def updatePath(self, source):
        if source == self.start:
            self._path = QtGui.QPainterPath(source.scenePos())
            self._path.lineTo(self.end.scenePos())
        else:
            self._path = QtGui.QPainterPath(self.start.scenePos())
            self._path.lineTo(source.scenePos())

        self.setPath(self._path)

    def arrowCalc(
        self, start_point=None, end_point=None
    ):  # calculates the point where the arrow should be drawn
        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self.start

            if endPoint is None:
                endPoint = self.end

            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx**2 + dy**2)
            normX, normY = dx / leng, dy / leng  # normalize

            # perpendicular vector
            perpX = -normY
            perpY = normX

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

        except (ZeroDivisionError, Exception):
            return None

    def directPath(self):
        path = QtGui.QPainterPath(self.start.scenePos())
        path.lineTo(self.end.scenePos())
        return path

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        painter.pen().setWidth(2)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

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

        if triangle_source is not None:
            painter.drawPolyline(triangle_source)

    def shape(self):
        shape = super().shape()
        shape.addRect(shape.boundingRect().adjusted(-5, -5, 5, 5))
        return shape

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec(event.screenPos())

        if action == delete_action:
            self.start.removeLine(self)
            self.end.removeLine(self)


class ControlPoint(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent):
        super().__init__(-5, -5, 10, 10, parent)
        self.parent = parent
        self.paths = []

        self.setAcceptHoverEvents(True)
        self.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges
        )

        self.setOpacity(0.3)
        self.clicked = False

    def addLine(self, pathItem):
        viable = self.newLineErrorCheck(pathItem)
        if viable:
            self.paths.append(pathItem)
            return True
        return False

    def newLineErrorCheck(self, pathItem):
        for existing in self.paths:
            if existing.controlPoints() == pathItem.controlPoints():
                return False

        def send_error(text):
            error_msg = QtWidgets.QMessageBox()
            error_msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            error_msg.setWindowTitle("Error in Path")
            error_msg.setText(text)
            error_msg.exec()

        if pathItem.start == self:
            rect_children_amt = len(self.parent.children)
            if rect_children_amt >= 1:
                if self.parent.state["Type"] != "Choice":
                    error_msg = "This type cannot connect to more than 1 state"
                    send_error(error_msg)
                    return False
                elif self.parent.state["Type"] == "Choice":
                    choices_amt = len(self.parent.state["Choices"])
                    if "Default" in self.parent.state.keys():
                        choices_amt += 1

                    if rect_children_amt >= choices_amt:
                        error_msg = f"This type cannot connect to more than {choices_amt} states"
                        send_error(error_msg)
                        return False
            self.parent.children.append(pathItem.end.parent)
        return True

    def removeLine(self, pathItem):
        for existing in self.paths:
            if existing.controlPoints() == pathItem.controlPoints():
                self.scene().removeItem(existing)
                self.paths.remove(existing)
                if pathItem.start == self:
                    self.parent.children.remove(pathItem.end.parent)
                return True
        return False

    def itemChange(self, change, value):
        for path in self.paths:
            path.updatePath(self)
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        self.setOpacity(1.0)

    def hoverLeaveEvent(self, event):
        self.setOpacity(0.3)


class CustomItem(QtWidgets.QGraphicsItem):
    pen = QtGui.QPen(QtGui.QColor(98, 99, 102, 255))
    controlBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))

    def __init__(self, state, left=False, right=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brush = QtGui.QBrush(QtGui.QColor(214, 127, 46))
        self.state = state
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.rect = QtCore.QRectF(0, 0, 100, 30)
        self.titleItem = QtWidgets.QGraphicsTextItem(parent=self)

        self.children = []
        self.controls = []
        self.initialize_ui()

    def initialize_ui(self):
        if "Title" not in self.state.keys():
            self.state["Title"] = ""
        title = self.state["Title"]

        self.titleItem.setHtml(f"<center>{title}</center>")

        max_width = 100
        self.titleItem.setTextWidth(max_width)

        self.titleRect = self.titleItem.boundingRect()
        text_width = self.titleRect.width()
        text_height = self.titleRect.height()

        diamond_width = text_width * 1.2
        diamond_height = text_height * 1.2

        self.rect.setRect(0, 0, diamond_width, diamond_height)

        self.titleRect.moveCenter(self.rect.center())
        self.titleItem.setPos(self.titleRect.topLeft())

        control_placements = [
            (self.rect.width() / 2, self.rect.height()),
            (self.rect.width(), self.rect.height() / 2),
            (self.rect.width() / 2, 0),
            (0, self.rect.height() / 2),
        ]

        if not self.controls:
            self.controls = [ControlPoint(self) for i in range(len(control_placements))]

        for i, control in enumerate(self.controls):
            control.setPen(self.pen)
            control.setBrush(self.controlBrush)
            control.setX(control_placements[i][0])
            control.setY(control_placements[i][1])

    def boundingRect(self):
        adjust = self.pen.width() / 2
        return self.rect.adjusted(-adjust, -adjust, adjust, adjust)

    def paint(self, painter, option, widget=None):
        painter.save()
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        if self.state["Type"] == "Choice":
            diamond_points = [
                QtCore.QPointF(self.rect.center().x(), self.rect.top()),
                QtCore.QPointF(self.rect.right(), self.rect.center().y()),
                QtCore.QPointF(self.rect.center().x(), self.rect.bottom()),
                QtCore.QPointF(self.rect.left(), self.rect.center().y()),
            ]
            painter.drawPolygon(QtGui.QPolygonF(diamond_points))
        else:
            painter.drawRoundedRect(self.rect, 4, 4)
        painter.restore()

    def setBrush(self, color="orange"):
        if color == "red":
            color = QtGui.QColor(214, 54, 64)
        elif color == "green":
            color = QtGui.QColor(10, 168, 89)
        else:
            color = QtGui.QColor(214, 127, 46)
        self.brush = QtGui.QBrush(color)
        self.update()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Delete")

        action = menu.exec(event.screenPos())

        if action == delete_action:
            objects_created = self.get_objects_created()
            all_objects_in_use = self.scene().getObjectsinUse()

            for created_object in objects_created:
                if created_object in all_objects_in_use:
                    self.sendError("Object created in use")
                    return

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
        error_msg = QtWidgets.QMessageBox()
        error_msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Error in State")
        error_msg.setText(text)
        error_msg.exec()

    def get_objects_created(self):
        if self.state["Type"] == "MethodCall":
            payloads = self.state["Payloads"]
            return [object_name for object_name in payloads]
        return []

    # get objects that are used in a state
    def get_objects_used(self):
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
        print(self.state)
        copy_of_state = dict(self.state)
        title = copy_of_state.pop("Title")
        state_string = json.dumps({title: copy_of_state}, indent=4)
        return state_string

    def set_state(self, new_state):
        self.state = new_state
        self.initialize_ui()

    def get_nexts(self):
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
    startItem = newConnection = None

    def controlPointAt(self, pos):
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
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            item = self.controlPointAt(event.scenePos())
            if item:
                self.startItem = item
                self.newConnection = Path(item, event.scenePos())
                self.addItem(self.newConnection)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
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
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and item != self.startItem:
                self.newConnection.setEnd(item)
                if self.startItem.addLine(self.newConnection):
                    item.addLine(self.newConnection)
                else:
                    # delete the connection if it exists; remove the following
                    # line if this feature is not required
                    self.startItem.removeLine(self.newConnection)
                    self.removeItem(self.newConnection)
            else:
                self.removeItem(self.newConnection)
        self.startItem = self.newConnection = None
        super().mouseReleaseEvent(event)

    def getObjectsinUse(self):
        rect_items = [item for item in self.items() if isinstance(item, CustomItem)]
        objects_in_use = []
        for rect_item in rect_items:
            rect_item_objects = rect_item.get_objects_used()
            for rect_item_object in rect_item_objects:
                objects_in_use.append(rect_item_object)
        return objects_in_use

    def getObjectsCreated(self):
        rect_items = [item for item in self.items() if isinstance(item, CustomItem)]
        objects_in_use = []
        for rect_item in rect_items:
            rect_item_objects = rect_item.get_objcts_created()
            for rect_item_object in rect_item_objects:
                objects_in_use.append(rect_item_object)
        return objects_in_use
