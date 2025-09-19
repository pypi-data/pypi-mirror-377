from typing import Optional, Any
import pathlib

from PySide6.QtGui import QPainter, QIcon
from PySide6.QtOpenGL import QOpenGLVertexArrayObject, QAbstractOpenGLFunctions

from .Layer import Layer
from ..TreeItemAttribute import TreeItemSliderAttribute, TreeItemFloatAttribute
from ...linalg import matrix
from ...Roles import Roles

class SwipeTool(Layer):
    kind = "swipe layer"
    icon: QIcon = QIcon()

    def __init__(self, name="Swipe tool", cutoff=0, dataset=None):
        super().__init__(name)
        if self.icon.isNull():
            # cannot be initialized in the class declaration because:
            # "QIcon needs a QGuiApplication instance before the icon is created." see QIcon doc
            SwipeTool.icon = QIcon("icons:swipetool.png")
        self.cutoff = cutoff
        self.dataset = dataset
        self.add_child(TreeItemSliderAttribute(self,
                                               "cutoff",
                                               tooltip="cutoff value",
                                               vmin=0.0,
                                               vmax=1.0))

    def data(self, column: int, role: int):
        if role == Roles.DatasetRole:
            return self.dataset
        return super().data(column, role)

    def update_show_params(self, params: Layer.ShowParams):
        params.cutoff = max(self.cutoff, params.cutoff)

    def show(self, view_matrix: matrix.Matrix, projection_matrix: matrix.Matrix, show_params: Layer.ShowParams,
             painter: Optional[QPainter] = None, vao: Optional[QOpenGLVertexArrayObject] = None,
             glfunc: Optional[QAbstractOpenGLFunctions] = None, blend: bool = True) -> None:
        """
        Swipe layers aren't shown as such, they only affect the layers above them
        """
        return None

    def to_dict(self, project_path: pathlib.Path) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict(project_path)
        output["cutoff"] = self.cutoff
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any], map_model: "MapModel") -> "SwipeTool":
        assert input_dict["kind"] == cls.kind
        assert "cutoff" in input_dict

        name = input_dict.get("name", "Swipe tool")
        cutoff = input_dict["cutoff"]
        layer = SwipeTool(name, cutoff, dataset = map_model.loader.dataset)
        if "visible" in input_dict:
            layer.visible = input_dict["visible"]
        return layer
