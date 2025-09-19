# -*- coding: utf-8 -*-

from typing import Any, Optional

from PySide6.QtCore import Qt

from PySide6.QtGui import QColor

from pyqtgraph.colormap import ColorMap

from insarviz.map.TreeModel import TreeItem, TreeModel

from insarviz.Roles import Roles


# TreeItemAttribute class ##########################################################################

class TreeItemAttribute(TreeItem):
    """
    TreeItemAttribute provides user-friendly access to a TreeItem's attribute. Used as a child of
    an item, it represents one of its attribute that can be modified by interacting with the
    TreeItemAttribute. TreeItemAttribute use getattr and setattr to get/set the attribute of its
    parent. LayerModel.setData is responsible to emit a dataChanged signal linked to the
    TreeItemAttribute's parent when the latter is modified.

    TreeItemAttribute.data(..., Roles.EditorRole) returns a string used by LayerView.ItemDelegate
    to create custom editor. TreeItemAttribute.data(..., Roles.DataRole) returns an insarviz.Roles
    included in the dataChanged emited by LayerModel.setData on the TreeItemAttribute's parent,
    this Roles is used for example by PlotModel to know if it has to recompute the data of
    a SelectionItem.

    Abstract class than need to be subclassed.
    """

    EditorRole: int = int(Roles.EditorRole)
    DataRole: int = int(Roles.DataRole)
    PersistentEditorWidgetRole: int = int(Roles.PersistentEditorWidgetRole)

    def __init__(self, parent: TreeItem, attribute_name: str, name: Optional[str] = None,
                 tooltip: Optional[str] = None, datarole: Optional[int] = None,
                 editable: bool = True):
        super().__init__(parent)
        assert parent, "TreeItemAttribute must have valid parent"
        try:
            getattr(parent, attribute_name)
        except AttributeError as e:
            raise AttributeError(f"TreeItemAttribute's parent must have an attribute matching \
                    attribute_name {attribute_name}\n{repr(e)}")
        self.attribute_name: str = attribute_name
        self.name: str
        if name is None:
            self.name = attribute_name
        else:
            self.name = name
        self.tooltip: Optional[str] = tooltip
        self.datarole: Optional[int] = datarole
        self.editable: bool = editable

    def data(self, column: int, role: int) -> Any:
        if column == TreeModel.remove_column:
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return f"{self.name} : {getattr(self.parent(), self.attribute_name)}"
        if role == Qt.ItemDataRole.ToolTipRole:
            return self.tooltip
        if role == TreeItemAttribute.DataRole:
            # used by LayerView.ItemDelegate to emit custom role in LayerModel.dataChanged
            return int(self.datarole) if self.datarole is not None else None
        if role == TreeItemAttribute.EditorRole:
            # must be implemented by subclasses and return a string that is used by
            # LayerView.ItemDelegate, this string shall not be None for self to be recognized
            # as a TreeItemAttribute in LayerModel
            raise NotImplementedError()
        return None

    def flags(self, flags: Qt.ItemFlags, column: int) -> Qt.ItemFlags:
        if column == 0 and self.editable:
            flags = flags | Qt.ItemFlag.ItemIsEditable
        elif column == TreeModel.remove_column:
            flags = flags & (~Qt.ItemFlag.ItemIsEnabled)
        return flags

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if column != 0:
            return False
        if role == Qt.ItemDataRole.EditRole:
            setattr(self.parent(), self.attribute_name, value)
            return True
        return False


class TreeItemIntegerAttribute(TreeItemAttribute):

    def __init__(self, parent: TreeItem, attribute_name: str, name: Optional[str] = None,
                 tooltip: Optional[str] = None, vmin: Optional[int] = None,
                 vmax: Optional[int] = None, unit: Optional[str] = None,
                 datarole: Optional[int] = None):
        super().__init__(parent, attribute_name, name=name, tooltip=tooltip, datarole=datarole)
        self.vmin: Optional[int] = vmin
        self.vmax: Optional[int] = vmax
        self.unit: Optional[str] = unit

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if self.unit:
                return f"{self.name} : {getattr(self.parent(), self.attribute_name)} {self.unit}"
        if role == Qt.ItemDataRole.EditRole:
            # (value, name, vmin, vmax, unit)
            return (getattr(self.parent(), self.attribute_name), self.name, self.vmin, self.vmax,
                    self.unit)
        if role == TreeItemAttribute.EditorRole:
            # used by LayerView.ItemDelegate to create custom editor
            return "integer"
        return super().data(column, role)

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if not isinstance(value, int):
            return False
        if self.vmin is not None:
            if value < self.vmin:
                return False
        if self.vmax is not None:
            if value > self.vmax:
                return False
        return super().set_data(value, column, role)


class TreeItemFloatAttribute(TreeItemAttribute):

    def __init__(self, parent: TreeItem, attribute_name: str, name: Optional[str] = None,
                 tooltip: Optional[str] = None, vmin: Optional[float] = None,
                 vmax: Optional[float] = None, unit: Optional[str] = None,
                 datarole: Optional[int] = None):
        super().__init__(parent, attribute_name, name=name, tooltip=tooltip, datarole=datarole)
        self.vmin: Optional[float] = vmin
        self.vmax: Optional[float] = vmax
        self.unit: Optional[str] = unit

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if self.unit:
                return f"{self.name} : {getattr(self.parent(), self.attribute_name)} {self.unit}"
        if role == Qt.ItemDataRole.EditRole:
            # (value, name, vmin, vmax, unit)
            return (getattr(self.parent(), self.attribute_name), self.name, self.vmin, self.vmax,
                    self.unit)
        if role == TreeItemAttribute.EditorRole:
            # used by LayerView.ItemDelegate to create custom editor
            return "float"
        return super().data(column, role)

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if not isinstance(value, float):
            return False
        if self.vmin is not None:
            if value < self.vmin:
                return False
        if self.vmax is not None:
            if value > self.vmax:
                return False
        return super().set_data(value, column, role)

class TreeItemSliderAttribute(TreeItemAttribute):

    def __init__(self, parent: TreeItem,
                 attribute_name: str, name: Optional[str] = None,
                 tooltip: Optional[str] = None, vmin: Optional[float] = None,
                 vmax: Optional[float] = None, datarole: Optional[int] = None):
        super().__init__(parent, attribute_name, name=name, tooltip=tooltip, datarole=datarole)
        self.vmin: Optional[float] = vmin
        self.vmax: Optional[float] = vmax
        self.persistent_editor = None

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            # Having None as a display role means the ItemDelegate
            # will create a persistent editor instead
            return None
        if role == Qt.ItemDataRole.EditRole:
            # (value, name, vmin, vmax)
            return (getattr(self.parent(), self.attribute_name), self.name, self.vmin, self.vmax)
        if role == Qt.ItemDataRole.SizeHintRole:
            if self.persistent_editor is not None:
                return self.persistent_editor.sizeHint()
        if role == TreeItemAttribute.EditorRole:
            # used by LayerView.ItemDelegate to create custom editor
            return "float_slider"
        if role == TreeItemAttribute.PersistentEditorWidgetRole:
            return self.persistent_editor
        return super().data(column, role)

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if role == TreeItemAttribute.PersistentEditorWidgetRole:
            if self.persistent_editor is None:
                self.persistent_editor = value
                return True
            else:
                return False

        if not isinstance(value, float):
            return False
        if self.vmin is not None:
            if value < self.vmin:
                return False
        if self.vmax is not None:
            if value > self.vmax:
                return False

        return super().set_data(value, column, role)

class TreeItemColorAttribute(TreeItemAttribute):

    def data(self, column: int, role: int) -> Any:
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return getattr(self.parent(), self.attribute_name)
        if role == TreeItemAttribute.EditorRole:
            # used by LayerView.ItemDelegate to create custom editor
            return "color"
        return super().data(column, role)

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if not isinstance(value, QColor):
            return False
        return super().set_data(value, column, role)


class TreeItemColormapAttribute(TreeItemAttribute):

    def data(self, column: int, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return getattr(self.parent(), self.attribute_name)
        if role == Qt.ItemDataRole.EditRole:
            return self.parent()
        if role == TreeItemAttribute.EditorRole:
            # used by LayerView.ItemDelegate to create custom editor
            return "colormap"
        return super().data(column, role)

    def set_data(self, value: Any, column: int, role: int) -> bool:
        if column != 0:
            return False
        if role == Qt.ItemDataRole.EditRole and isinstance(value, tuple):
            if len(value) != 3:
                return False
            colormap, v0, v1 = value
            if ((not isinstance(colormap, ColorMap)) or (not isinstance(v0, float)) or
                    (not isinstance(v1, float))):
                return False
            self.parent().set_colormap(colormap)
            self.parent().set_v0_v1(v0, v1)
            return True
        return False
