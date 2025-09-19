# -*- coding: utf-8 -*-

# imports ##########################################################################################

from typing import Any, Optional

import pathlib

from PySide6.QtCore import Qt, QRectF, QPointF, QEasingCurve

from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen

from PySide6.QtOpenGL import QAbstractOpenGLFunctions, QOpenGLVertexArrayObject

from insarviz.map.layers.Layer import Layer

from insarviz.map.TreeItemAttribute import TreeItemColorAttribute, TreeItemIntegerAttribute

from insarviz.map.TreeModel import TreeItem, TreeModel

from insarviz.linalg import matrix, vector

from insarviz import bresenham

from insarviz.Roles import Roles


# SelectionLayer class #############################################################################

class SelectionLayer(Layer):
    removable: bool = False
    renamable: bool = False
    kind: str = "selection layer"

    def __init__(self):
        super().__init__("Selection Layer")
        self.points_folder = SelectionFolder("Points", icon=QIcon('icons:points.png'))
        self.add_child(self.points_folder, 0)
        self.profiles_folder = SelectionFolder("Spatial profiles", icon=QIcon('icons:profile.png'))
        self.add_child(self.profiles_folder, 1)
        self.references_folder = SelectionFolder("References", icon=QIcon('icons:ref.png'))
        self.add_child(self.references_folder, 2)

    def data(self, column: int, role: int) -> Any:
        if column == 0 and role == Qt.ItemDataRole.ToolTipRole:
            return "Selection layer, points, spatial profiles and references"
        return super().data(column, role)

    def show(self, view_matrix: matrix.Matrix, projection_matrix: matrix.Matrix, show_params: Layer.ShowParams,
             painter: Optional[QPainter] = None, vao: Optional[QOpenGLVertexArrayObject] = None,
             glfunc: Optional[QAbstractOpenGLFunctions] = None, blend: bool = True) -> None:
        # pylint: disable=unused-argument
        assert painter is not None
        for reference in self.references_folder.child_items:
            if reference.visible:
                reference.show(view_matrix, painter)
        for profile in self.profiles_folder.child_items:
            if profile.visible:
                profile.show(view_matrix, painter)
        for point in self.points_folder.child_items:
            if point.visible:
                point.show(view_matrix, painter)

    def to_dict(self, project_path: pathlib.Path) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict(project_path)
        output["points"] = [point.to_dict() for point in self.points_folder.child_items]
        output["profiles"] = [profile.to_dict() for profile in self.profiles_folder.child_items]
        output["references"] = [ref.to_dict() for ref in self.references_folder.child_items]
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any]) -> "SelectionLayer":
        assert input_dict["kind"] == cls.kind
        selection_layer = SelectionLayer()
        if "visible" in input_dict:
            selection_layer.visible = input_dict["visible"]
        for point in input_dict["points"]:
            selection_layer.points_folder.add_child(SelectionPoint.from_dict(point))
        for profile in input_dict["profiles"]:
            selection_layer.profiles_folder.add_child(SelectionProfile.from_dict(profile))
        for ref in input_dict["references"]:
            selection_layer.references_folder.add_child(SelectionReference.from_dict(ref))
        return selection_layer


# SelectionFolder class ############################################################################

class SelectionFolder(TreeItem):

    def __init__(self, name: str = "", icon: Optional[QIcon] = None):
        super().__init__()
        self.name = name
        if icon is None:
            icon = QIcon()
        self.icon = icon

    def data(self, column: int, role: int):
        if column == TreeModel.remove_column:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self.name
        if role == Qt.ItemDataRole.DecorationRole:
            return self.icon
        if role == Roles.FolderRole:
            # used by LayerView.ProxyLayerModel
            return "SELECTION_FOLDER"
        return None

    def set_data(self, value: Any, column: int, role: int) -> bool:
        return False

    def flags(self, flags: Qt.ItemFlags, column: int) -> Qt.ItemFlags:
        return flags


# SelectionItem classes ############################################################################

def location_path() -> QPainterPath:
    path = QPainterPath()
    path.moveTo(38., 80.)
    path.cubicTo(35., 62., 26., 60., 20., 50.)
    path.cubicTo(0., 0., 80., 0., 60., 50.)
    path.cubicTo(54., 60., 48., 62., 45., 80.)
    path.lineTo(38., 80.)
    return path


def easing_location() -> QEasingCurve:
    easing = QEasingCurve(QEasingCurve.Type.BezierSpline)
    easing.addCubicBezierSegment(QPointF(0.6, 1.), QPointF(0.7, 1.), QPointF(1., 1.))
    return easing


def world_to_view(rect: tuple[int, int, int, int], view_matrix: matrix.Matrix) -> QRectF:
    (left, top, right, bottom) = rect
    left_top_data = vector.matrix((float(left), float(top), 0., 1.))
    left_top_view = matrix.product(view_matrix, left_top_data)
    left_top_view = left_top_view[0][0], left_top_view[1][0]
    # we use right+1 and bottom+1 because we want to fill up to the start of the next pixel
    right_bottom_data = vector.matrix((float(right+1), float(bottom+1), 0., 1.))
    right_bottom_view = matrix.product(view_matrix, right_bottom_data)
    right_bottom_view = right_bottom_view[0][0], right_bottom_view[1][0]
    return QRectF(QPointF(*left_top_view), QPointF(*right_bottom_view))


class SelectionItem(TreeItem):

    ShowCurveRole: int = int(Roles.ShowCurveRole)
    icon: QIcon = QIcon()
    location_icon: QPainterPath = location_path()
    easing_function_loc_icon = easing_location()
    loc_icon_scaling = 0.5
    loc_icon_area_threshold = 25
    loc_icon_area_end_easing = 4

    def __init__(self, name: str = ""):
        super().__init__()
        self.name: str = name
        self.visible: bool = True
        self.show_curve: bool = True
        self.color: QColor = QColor()

    def data(self, column: int, role: int) -> Any:
        if column == TreeModel.remove_column:
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self.name
        if role == Qt.ItemDataRole.DecorationRole:
            return self.color
        if role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked if self.visible else Qt.CheckState.Unchecked
        if role == self.ShowCurveRole:
            return Qt.CheckState.Checked if self.show_curve else Qt.CheckState.Unchecked
        return None

    def flags(self, flags: Qt.ItemFlags, column: int) -> Qt.ItemFlags:
        if column == 0:
            # UserCheckable => visibility, Editable => change name
            flags = flags | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable
        # Editable => remove
        return flags | Qt.ItemFlag.ItemIsEditable

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if column != 0:
            return False
        if role == Qt.ItemDataRole.CheckStateRole:
            self.visible = (value == Qt.CheckState.Checked or value == Qt.CheckState.Checked.value)
            return True
        if role == self.ShowCurveRole:
            self.show_curve = (value == Qt.CheckState.Checked or value == Qt.CheckState.Checked.value)
            return True
        if role == Qt.ItemDataRole.EditRole:
            self.name = value
            return True
        return False

    def show(self, view_matrix: matrix.Matrix, painter: QPainter, preview: bool = False) -> None:
        """
        Display the layer using either OpenGL commands or painter

        Qpainter documentation on coordinate system : https://doc.qt.io/qt-5/coordsys.html.

        Parameters
        ----------
        view_matrix : matrix.Matrix
            Transform world coordinates into view coordinates.
        painter : QPainter
            QPainter provided by the view.
        preview : bool
            True if the selection item is being constructed
            False if the selection item is in the selection layer
        """
        rect_list = self.get_rect()
        for rect in rect_list:
            view_rect = world_to_view(rect, view_matrix)
            painter.fillRect(view_rect, self.color)
            # location icon only for single rect
            if len(rect_list) == 1:
                area = view_rect.width() * view_rect.height()
                if area < self.loc_icon_area_threshold:
                    painter.save()
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                    painter.setBrush(self.color)
                    painter.setPen(QPen(self.color.darker(140), 2))
                    painter.translate(view_rect.center())
                    if area > self.loc_icon_area_end_easing:
                        easing_progress = (self.loc_icon_area_threshold - area) / \
                            (self.loc_icon_area_threshold - self.loc_icon_area_end_easing)
                        scale = self.loc_icon_scaling * \
                            self.easing_function_loc_icon.valueForProgress(easing_progress)
                    else:
                        scale = self.loc_icon_scaling
                    painter.scale(scale, scale)
                    painter.translate(-QPointF(self.location_icon.boundingRect().center().x(),
                                               self.location_icon.boundingRect().bottom()))
                    painter.drawPath(self.location_icon)
                    self.icon.paint(painter, 24, 18, 32, 32,
                                    alignment=Qt.AlignmentFlag.AlignCenter, state=QIcon.State.On)
                    painter.restore()

    def get_rect(self) -> list[tuple[int, int, int, int]]:
        """
        Shall be implemented by subclasses.
        return (left, top, right, bottom)
        """
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output["kind"] = self.kind
        output["name"] = self.name
        output["color"] = self.color.name()
        output["visible"] = self.visible
        output["show_curve"] = self.show_curve
        return output

    def init_from_dict(self, input_dict: dict[str, Any]) -> None:
        self.name = input_dict["name"]
        self.color = QColor(input_dict["color"])
        self.visible = input_dict["visible"]
        self.show_curve = input_dict["show_curve"]


class SelectionPoint(SelectionItem):

    kind: str = "point"
    count: int = 0

    def __init__(self, x: int, y: int, r: int):
        SelectionPoint.count += 1
        if self.icon.isNull():
            # cannot be initialized in the class declaration because:
            # "QIcon needs a QGuiApplication instance before the icon is created." see QIcon doc
            SelectionPoint.icon = QIcon('icons:points.png')
        super().__init__(f"Point {self.count}")
        self.x: int = x
        self.y: int = y
        self.r: int = r
        self.add_child(TreeItemIntegerAttribute(self, "r", name="radius",
                                                tooltip="radius in pixels", vmin=1, vmax=1000,
                                                unit="px", datarole=Roles.ComputeDataRole))
        self.color = QColor("blue")
        self.add_child(TreeItemColorAttribute(self, "color", tooltip="color",
                                              datarole=Roles.CurveColorRole))

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"Point at ({self.x},{self.y})"
        return super().data(column, role)

    def get_rect(self) -> list[tuple[int, int, int, int]]:
        return [(self.x-self.r+1, self.y-self.r+1, self.x+self.r-1, self.y+self.r-1)]

    def set_r(self, r: int) -> None:
        """Set radius."""
        self.r = r

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict()
        output["x"] = self.x
        output["y"] = self.y
        output["r"] = self.r
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any]) -> "SelectionPoint":
        assert input_dict["kind"] == cls.kind
        point = cls(input_dict["x"], input_dict["y"], input_dict["r"])
        point.init_from_dict(input_dict)
        return point


class SelectionProfile(SelectionItem):

    kind: str = "profile"
    count: int = 0
    thickness_threshold = 2
    TemporalRole = Roles.ProfileTemporalRole
    SpatialRole = Roles.ProfileSpatialRole
    temporal_icon: QIcon = QIcon()
    spatial_icon: QIcon = QIcon()

    def __init__(self, x: int, y: int, r: int):
        SelectionProfile.count += 1
        if self.icon.isNull():
            # cannot be initialized in the class declaration because:
            # "QIcon needs a QGuiApplication instance before the icon is created." see QIcon doc
            SelectionProfile.icon = QIcon('icons:profile.png')
            SelectionProfile.temporal_icon = QIcon('icons:temporal.svg')
            SelectionProfile.spatial_icon = QIcon('icons:spatial.svg')
        super().__init__(f"Profile {self.count}")
        self.points: list[tuple[int, int]] = [(x, y)]
        self.temporal_point: Optional[int] = None
        self.spatial_point: Optional[int] = None
        self.r: int = r
        self.add_child(TreeItemIntegerAttribute(self, "r", name="radius",
                                                tooltip="radius in pixels", vmin=1, vmax=1000,
                                                unit="px", datarole=Roles.ComputeDataRole))
        self.color = QColor("orchid")
        self.add_child(TreeItemColorAttribute(self, "color", tooltip="color",
                                              datarole=Roles.CurveColorRole))

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.ToolTipRole:
            point_list: str = ', '.join('({}, {})'.format(*p) for p in self.points)
            return f"Profile {point_list}"
        return super().data(column, role)

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if role == self.TemporalRole:
            self.temporal_point = value
            return True
        if role == self.SpatialRole:
            self.spatial_point = value
            return True
        return super().set_data(value, column, role)

    def get_rect(self) -> list[tuple[int, int, int, int]]:
        result = []
        for i in range(1, len(self.points)):
            for k in bresenham.line(self.points[i-1][0], self.points[i-1][1], self.points[i][0],
                                    self.points[i][1]):
                result.append((k[0]-self.r+1, k[1]-self.r+1, k[0]+self.r-1, k[1]+self.r-1))
        return result

    def show(self, view_matrix: matrix.Matrix, painter: QPainter, preview: bool = False) -> None:
        for rect in self.get_rect():
            view_rect = world_to_view(rect, view_matrix)
            if view_rect.width() < self.thickness_threshold:
                thickness_change = (self.thickness_threshold - view_rect.width())/2
                view_rect.adjust(-thickness_change, -thickness_change,
                                 thickness_change, thickness_change)
            painter.fillRect(view_rect, self.color)
        if self.temporal_point is not None:
            assert self.temporal_point in range(len(self.get_rect()))
            view_rect = world_to_view(self.get_rect()[self.temporal_point], view_matrix)
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setBrush(self.color)
            painter.setPen(QPen(self.color.darker(140), 2))
            painter.translate(view_rect.center())
            scale = self.loc_icon_scaling
            painter.scale(scale, scale)
            painter.translate(-QPointF(self.location_icon.boundingRect().center().x(),
                                       self.location_icon.boundingRect().bottom()))
            painter.drawPath(self.location_icon)
            self.temporal_icon.paint(painter, 24, 18, 32, 32,
                                     alignment=Qt.AlignmentFlag.AlignCenter, state=QIcon.State.On)
            painter.restore()
        if self.spatial_point is not None:
            assert self.spatial_point in range(len(self.get_rect()))
            view_rect = world_to_view(self.get_rect()[self.spatial_point], view_matrix)
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setBrush(self.color)
            painter.setPen(QPen(self.color.darker(140), 2))
            painter.translate(view_rect.center())
            scale = self.loc_icon_scaling
            painter.scale(scale, scale)
            painter.translate(-QPointF(self.location_icon.boundingRect().center().x(),
                                       self.location_icon.boundingRect().bottom()))
            painter.drawPath(self.location_icon)
            self.spatial_icon.paint(painter, 24, 18, 32, 32,
                                    alignment=Qt.AlignmentFlag.AlignCenter, state=QIcon.State.On)
            painter.restore()

    def add_point(self, x: int, y: int) -> None:
        self.points.append((x, y))

    def remove_last_point(self) -> None:
        del self.points[-1]

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict()
        output["points"] = self.points
        output["r"] = self.r
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any]) -> "SelectionProfile":
        assert input_dict["kind"] == cls.kind
        assert len(input_dict["points"]) > 1
        profile = cls(input_dict["points"][0][0], input_dict["points"][0][1], input_dict["r"])
        for point in input_dict["points"][1:]:
            profile.add_point(point[0], point[1])
        profile.init_from_dict(input_dict)
        return profile


class SelectionReference(SelectionItem):

    kind: str = "reference"
    count: int = 0

    def __init__(self, x: int, y: int):
        SelectionReference.count += 1
        if self.icon.isNull():
            # cannot be initialized in the class declaration because:
            # "QIcon needs a QGuiApplication instance before the icon is created." see QIcon doc
            SelectionReference.icon = QIcon('icons:ref.png')
        super().__init__(f"Reference {self.count}")
        self.left: int = x
        self.right: int = x
        self.top: int = y
        self.bottom: int = y
        self.color = QColor("orange")
        self.add_child(TreeItemColorAttribute(self, "color", tooltip="color",
                                              datarole=Roles.CurveColorRole))

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"Reference from ({self.left}, {self.top}) to ({self.right}, {self.bottom})"
        return super().data(column, role)

    def get_rect(self) -> list[tuple[int, int, int, int]]:
        return [(self.left, self.top, self.right, self.bottom)]

    def set_rect(self, left: int, top: int, right: int, bottom: int) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict()
        output["left"] = self.left
        output["right"] = self.right
        output["top"] = self.top
        output["bottom"] = self.bottom
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any]) -> "SelectionReference":
        assert input_dict["kind"] == cls.kind
        ref = cls(input_dict["left"], input_dict["top"])
        ref.set_rect(input_dict["left"], input_dict["top"], input_dict["right"],
                     input_dict["bottom"])
        ref.init_from_dict(input_dict)
        return ref
