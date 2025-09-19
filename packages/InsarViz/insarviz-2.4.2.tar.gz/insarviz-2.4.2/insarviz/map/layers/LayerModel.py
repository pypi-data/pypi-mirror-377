# -*- coding: utf-8 -*-

"""
LayerModel

This module contains the LayerModel class managing the layers of the Map view.
"""

# imports ##########################################################################################

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Iterable

import gc

from PySide6.QtCore import (
    Qt, Slot, Signal, QModelIndex, QMimeData, QByteArray
)

from PySide6.QtGui import QUndoCommand

from insarviz.map.TreeModel import TreeModel, TreeItem

from insarviz.Roles import Roles

from insarviz.map.layers.Layer import Layer

if TYPE_CHECKING:
    from insarviz.map.SelectionLayer import (
        SelectionLayer, SelectionPoint, SelectionProfile, SelectionReference)


# LayerModel class #################################################################################

class LayerModel(TreeModel):
    """
    Model class managing the layers. Follows a tree structure, with first column being the items
    themselves and second column being remove buttons. The children of the root are the Layers.
    Children of layers can be TreeItemAttribute that provide user-friendly access to a TreeItem's
    attribute, or SelectionFolder and recursively SelectionItem in the case of the SelectionLayer.
    Only layer items (at the root of the tree) can be dragged and dropped. An item's checkbox
    manages the visibility of the item in MapView (displayed if checked, hidden if unchecked).
    All actions modifying LayerModel (add, remove, move or modify item) are wrapped inside a
    QUndoCommand that is pushed on the ts_viz.MainWindow's QUndoStack.
    """

    # connected to ts_viz.MainWindow.layer_remove_action.setEnabled
    current_removable = Signal(bool)
    # connected to ts_viz.MainWindow.layer_moveup_action.setEnabled
    current_movable_up = Signal(bool)
    # connected to ts_viz.MainWindow.layer_movedown_action.setEnabled
    current_movable_down = Signal(bool)
    # connected to PlotModel.on_selection_init and to ts_viz.MainWindow.undo_stack.clear
    selection_initialized = Signal(object)  # object = self
    # connected to LayerView.expand
    request_expand = Signal(QModelIndex)
    # connected to ts_viz.MainWindow.undo_stack.push
    add_undo_command = Signal(QUndoCommand)
    # connected to MapModel.request_paint
    request_paint = Signal()

    def __init__(self, layers: Optional[list[Layer]] = None):
        super().__init__()
        if layers is not None:
            for layer in layers:
                self.add_layer(layer)
        # direct access to layers
        self.layers: list[Layer] = self.root_item.child_items
        self.selection: Optional[SelectionLayer] = None

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # first column is the items themselves (layer, selection item, etc.)
        # second column is the remove buttons
        return 2

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        result: bool = super().setData(index, value, role)
        editor_role: str = index.data(Roles.EditorRole)
        if result is True and editor_role is not None:
            # if editor_role is not None then index is a TreeItemAttribute, and we need to signal
            # that index.parent() has been modified
            roles: list[int] = [Qt.ItemDataRole.EditRole]
            # get the data role of the TreeItemAttribute, that is an indication of what has changed
            # in its parent (color, name, position...)
            data_role: Optional[int] = index.data(Roles.DataRole)
            if data_role is not None:
                roles += [data_role]
            # emit a dataChanged signal of what has changed in the parent (catched by PlotModel
            # for example)
            self.dataChanged.emit(index.parent(), index.parent(), roles)
        return result

    def clear(self) -> None:
        super().clear()
        # force garbage collection
        gc.collect()

    # reimplemented methods for drag and drop
    # multiple selection is disabled, so indexes is assumed to contain an unique index

    def mimeTypes(self) -> list[str]:
        # tiff and insarviz.layer drops are accepted
        return ['image/tiff', 'application/insarviz.layer']

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        indexes = iter(indexes)
        try:
            index = next(indexes)
        except StopIteration:
            raise RuntimeError("LayerModel: empty drag")  # pylint: disable=raise-missing-from
        try:
            next(indexes)
            raise RuntimeError("LayerModel: drag of more than one row is forbidden")
        except StopIteration:
            pass
        assert index.isValid() and not index.parent().isValid(), \
            "LayerModel : drag of a row that is not a top child (i.e. layer) is forbidden"
        mime_data: QMimeData = QMimeData()
        # store the row number in mimeData.text
        mime_data.setText(str(index.row()))
        # create an 'application/insarviz.layer' entry in mimeData.formats using a dummy QByteArray
        mime_data.setData('application/insarviz.layer', QByteArray())
        return mime_data

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int,
                        parent: QModelIndex) -> bool:
        # intersection between data.formats and self.mimeTypes() is empty
        # or intersection between action and self.supportedDropActions() is empty
        if (not set(data.formats()) & set(self.mimeTypes()) or
                not action & self.supportedDropActions()):
            return False
        # dropped on root or directly on layer item
        if not parent.isValid() or (not parent.parent().isValid() and row == -1 and column == -1):
            if data.hasFormat('application/insarviz.layer') and action == Qt.DropAction.MoveAction:
                return True
            elif data.hasFormat('image/tiff') and action == Qt.DropAction.CopyAction:
                return True
            else:
                return False
        else:
            return False

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int,
                     parent: QModelIndex) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent):
            return False
        if action == Qt.DropAction.IgnoreAction:
            return True
        if column > 0:
            column = 0
        if parent.isValid():
            # dropping on an item (i.e. not on root)
            if not parent.parent().isValid() and row == -1:
                # dropping on a layer
                row = parent.row() + 1
                parent = QModelIndex()  # i.e. root
            else:
                return False
        elif row == -1:
            # dropping on root and not between layers
            row = self.rowCount(parent)
        if data.hasFormat('application/insarviz.layer'):
            # "data.layer" is the row that we are dragging and "row" is the row we are dropping on
            self.add_undo_command.emit(MoveLayerCommand(self, int(data.text()), row))
            return True
        return False

    # custom methods

    @Slot(object, int)
    def add_layer(self, layer: Layer, i: int = -1) -> None:
        """
        Add layer at i-th row. If i=-1 append layer at the end.
        """
        self.add_undo_command.emit(AddLayerCommand(self, layer, i))

    # connected to LayerView.selectionModel().currentChanged
    @Slot(QModelIndex)
    def manage_current_changed(self, index: QModelIndex) -> None:
        """
        Reacts to change of current selected item in LayerView by emiting signals about whether
        the new selected item is removable / movable up / movable down.
        """
        index = index.siblingAtColumn(self.remove_column)
        if not index.isValid():
            # root item
            self.current_removable.emit(False)
            self.current_movable_up.emit(False)
            self.current_movable_down.emit(False)
        else:
            if index.flags() & Qt.ItemFlag.ItemIsEditable:
                self.current_removable.emit(True)
            else:
                self.current_removable.emit(False)
            if not index.parent().isValid():
                # layer item (parent is root)
                if index.row() == 0:
                    self.current_movable_up.emit(False)
                else:
                    self.current_movable_up.emit(True)
                if index.row() == self.rowCount(index.parent()) - 1:
                    self.current_movable_down.emit(False)
                else:
                    self.current_movable_down.emit(True)
            else:
                self.current_movable_up.emit(False)
                self.current_movable_down.emit(False)

    # connected to MainWindow.layer_showall_action.triggered
    @Slot()
    def show_all_layers(self) -> None:
        for i in range(self.root_item.child_count()):
            index: QModelIndex = self.index(i, 0, QModelIndex())
            self.setData(index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)

    # connected to MainWindow.layer_hideall_action.triggered
    @Slot()
    def hide_all_layers(self) -> None:
        for i in range(self.root_item.child_count()):
            index: QModelIndex = self.index(i, 0, QModelIndex())
            self.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)

    # connected to MainWindow.layer_moveup_action.triggered
    @Slot(QModelIndex)
    def move_layer_up(self, index: QModelIndex) -> None:
        """
        Move up the layer at index (towards row 0 which is the uppest row).
        """
        if index.parent() == QModelIndex() and index.row() != 0:
            self.add_undo_command.emit(MoveLayerCommand(self, index.row(), index.row()-1))

    # connected to MainWindow.layer_movedown_action.triggered
    @Slot(QModelIndex)
    def move_layer_down(self, index: QModelIndex) -> None:
        """
        Move down the layer at index (towards row self.rowCount(index.parent()) which is the
        lowest row).
        """
        if index.parent() == QModelIndex() and index.row() != self.rowCount(index.parent()) - 1:
            self.add_undo_command.emit(MoveLayerCommand(self, index.row(), index.row()+2))

    # connected to MainWindow.layer_remove_action.triggered, also called by LayerView.remove
    @Slot(QModelIndex)
    def remove(self, index: QModelIndex) -> None:
        """
        Remove the item at index.
        """
        self.add_undo_command.emit(RemoveTreeItemCommand(self, index.row(), index.parent()))

    # called by MapModel after adding selection layer
    def set_selection(self, selection: SelectionLayer) -> None:
        self.selection = selection
        self.selection_initialized.emit(self)

    def add_selection_point(self, point: SelectionPoint) -> None:
        """
        Add a selection point at the end of the point folder.
        """
        self.add_undo_command.emit(AddSelectionPointCommand(self, point))

    def add_selection_profile(self, profile: SelectionProfile) -> None:
        """
        Add a selection profile at the end of the profile folder.
        """
        self.add_undo_command.emit(AddSelectionProfileCommand(self, profile))

    def add_selection_reference(self, reference: SelectionReference) -> None:
        """
        Add a selection reference at the end of the reference folder.
        """
        self.add_undo_command.emit(AddSelectionReferenceCommand(self, reference))

    def get_lineage(self, index: QModelIndex) -> list[int]:
        """
        Return the lineage of index: the child numbers of the path to reach it from the root.
        For example, if index is the third child of the first child of the root:
        self.get_lineage(index) = [0, 2]

        Used to store the index of an item in QUndoCommands. Indeed QModelIndex shall not be stored
        and QPersistentIndex is no longer valid if the item has been removed (even if this remove
        is later undone).
        """
        lineage: list[int] = []
        while index.isValid():
            lineage.insert(0, index.row())
            index = index.parent()
        return lineage

    def get_index_from_lineage(self, lineage: Iterable[int]) -> QModelIndex:
        """
        Return a QModelIndex from a lineage created by LayerModel.get_lineage.
        """
        index: QModelIndex = QModelIndex()
        for i in lineage:
            index = self.index(i, 0, index)
        return index


# QUndoCommand classes #############################################################################

class SetDataCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, index: QModelIndex, value: Any, role: int,
                 parent_command: Optional[QUndoCommand] = None,
                 old_value: Any = None):
        super().__init__(parent_command)
        if index.data(Roles.EditorRole) is not None:
            # index is a TreeItemAttribute
            self.setText(
                f"Change {index.data(Qt.ItemDataRole.ToolTipRole)} of {index.parent().data(Qt.ItemDataRole.DisplayRole)}")
        else:
            self.setText(f"Change name of {index.data(Qt.ItemDataRole.DisplayRole)}")
        self.layer_model: LayerModel = layer_model
        self.lineage: list[int] = layer_model.get_lineage(index)
        self.new_value: Any = value
        self.role: int = role
        self.old_value: Any
        if index.data(Roles.EditorRole) in ("integer", "float", "float_slider"):
            self.old_value = self.layer_model.data(index, role)[0] if old_value is None else old_value
        elif index.data(Roles.EditorRole) == "colormap":
            old_colormap = self.layer_model.data(index, Qt.ItemDataRole.DisplayRole)
            layer = self.layer_model.data(index, Qt.ItemDataRole.EditRole)
            old_v0, old_v1 = layer.colormap_v0, layer.colormap_v1
            self.old_value = (old_colormap, old_v0, old_v1)
        else:
            self.old_value = self.layer_model.data(index, role)

    def redo(self) -> None:
        index: QModelIndex = self.layer_model.get_index_from_lineage(self.lineage)
        if not index.isValid():
            raise RuntimeError("SetDataCommand: invalid lineage")
        if not self.layer_model.setData(index, self.new_value, self.role):
            self.setObsolete(True)

    def undo(self) -> None:
        index: QModelIndex = self.layer_model.get_index_from_lineage(self.lineage)
        if not index.isValid():
            raise RuntimeError("SetDataCommand: invalid lineage")
        self.layer_model.setData(index, self.old_value, self.role)


class AddLayerCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, layer: Layer, index: int = -1,
                 parent_command: Optional[QUndoCommand] = None):
        super().__init__(parent_command)
        self.setText(f"Add layer {layer.name}")
        self.layer_model: LayerModel = layer_model
        self.layer: Layer = layer
        self.index: int = index

    def redo(self) -> None:
        if not self.layer_model.add_item(self.layer, self.index, QModelIndex()):
            self.setObsolete(True)
        else:
            self.layer.request_paint.connect(self.layer_model.request_paint)

    def undo(self) -> None:
        self.layer_model.remove_item(self.index, QModelIndex())
        self.layer.request_paint.disconnect(self.layer_model.request_paint)


class AddSelectionPointCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, point: SelectionPoint,
                 parent_command: Optional[QUndoCommand] = None):
        super().__init__(parent_command)
        self.setText(f"Add point {point.name}")
        self.layer_model: LayerModel = layer_model
        self.point: SelectionPoint = point

    def redo(self) -> None:
        assert self.layer_model.selection is not None
        selection_index: QModelIndex = self.layer_model.index(
            self.layer_model.selection.child_number(), 0, QModelIndex())
        assert selection_index.isValid()
        points_folder: QModelIndex = self.layer_model.index(
            self.layer_model.selection.points_folder.child_number(), 0, selection_index)
        assert points_folder.isValid()
        if self.layer_model.add_item(self.point, -1, points_folder):
            self.layer_model.request_expand.emit(selection_index)
            self.layer_model.request_expand.emit(points_folder)
        else:
            self.setObsolete(True)

    def undo(self) -> None:
        assert self.layer_model.selection is not None
        selection_index: QModelIndex = self.layer_model.index(
            self.layer_model.selection.child_number(), 0, QModelIndex())
        assert selection_index.isValid()
        points_folder: QModelIndex = self.layer_model.index(
            self.layer_model.selection.points_folder.child_number(), 0, selection_index)
        assert points_folder.isValid()
        self.layer_model.remove_item(self.point.child_number(), points_folder)


class AddSelectionProfileCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, profile: SelectionProfile,
                 parent_command: Optional[QUndoCommand] = None):
        super().__init__(parent_command)
        self.setText(f"Add profile {profile.name}")
        self.layer_model: LayerModel = layer_model
        self.profile: SelectionProfile = profile

    def redo(self) -> None:
        assert self.layer_model.selection is not None
        selection_index: QModelIndex = self.layer_model.index(
            self.layer_model.selection.child_number(), 0, QModelIndex())
        assert selection_index.isValid()
        profiles_folder: QModelIndex = self.layer_model.index(
            self.layer_model.selection.profiles_folder.child_number(), 0, selection_index)
        assert profiles_folder.isValid()
        if self.layer_model.add_item(self.profile, -1, profiles_folder):
            self.layer_model.request_expand.emit(selection_index)
            self.layer_model.request_expand.emit(profiles_folder)
        else:
            self.setObsolete(True)

    def undo(self) -> None:
        assert self.layer_model.selection is not None
        selection_index: QModelIndex = self.layer_model.index(
            self.layer_model.selection.child_number(), 0, QModelIndex())
        assert selection_index.isValid()
        profiles_folder: QModelIndex = self.layer_model.index(
            self.layer_model.selection.profiles_folder.child_number(), 0, selection_index)
        assert profiles_folder.isValid()
        self.layer_model.remove_item(self.profile.child_number(), profiles_folder)


class AddSelectionReferenceCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, reference: SelectionReference,
                 parent_command: Optional[QUndoCommand] = None):
        super().__init__(parent_command)
        self.setText(f"Add reference {reference.name}")
        self.layer_model: LayerModel = layer_model
        self.reference: SelectionReference = reference

    def redo(self) -> None:
        assert self.layer_model.selection is not None
        selection_index: QModelIndex = self.layer_model.index(
            self.layer_model.selection.child_number(), 0, QModelIndex())
        assert selection_index.isValid()
        references_folder: QModelIndex = self.layer_model.index(
            self.layer_model.selection.references_folder.child_number(), 0, selection_index)
        assert references_folder.isValid()
        if self.layer_model.add_item(self.reference, -1, references_folder):
            self.layer_model.request_expand.emit(selection_index)
            self.layer_model.request_expand.emit(references_folder)
        else:
            self.setObsolete(True)

    def undo(self) -> None:
        assert self.layer_model.selection is not None
        selection_index: QModelIndex = self.layer_model.index(
            self.layer_model.selection.child_number(), 0, QModelIndex())
        assert selection_index.isValid()
        references_folder: QModelIndex = self.layer_model.index(
            self.layer_model.selection.references_folder.child_number(), 0, selection_index)
        assert references_folder.isValid()
        self.layer_model.remove_item(self.reference.child_number(), references_folder)


class RemoveTreeItemCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, index: int, parent: QModelIndex,
                 parent_command: Optional[QUndoCommand] = None):
        super().__init__(parent_command)
        item_index: QModelIndex = layer_model.index(index, 0, parent)
        self.item: TreeItem = layer_model.get_item(item_index)
        self.setText(f"Remove {self.item.kind} {self.item.name}")
        self.layer_model: LayerModel = layer_model
        self.lineage: list[int] = layer_model.get_lineage(item_index)

    def redo(self) -> None:
        parent: QModelIndex = self.layer_model.get_index_from_lineage(self.lineage[:-1])
        if not self.layer_model.remove_item(self.lineage[-1], parent):
            self.setObsolete(True)

    def undo(self) -> None:
        parent: QModelIndex = self.layer_model.get_index_from_lineage(self.lineage[:-1])
        self.layer_model.add_item(self.item, self.lineage[-1], parent)
        while parent.isValid():
            self.layer_model.request_expand.emit(parent)
            parent = parent.parent()


class MoveLayerCommand(QUndoCommand):

    def __init__(self, layer_model: LayerModel, start: int, target: int,
                 parent_command: Optional[QUndoCommand] = None):
        super().__init__(parent_command)
        layer: TreeItem = layer_model.get_item(layer_model.index(start, 0, QModelIndex()))
        assert isinstance(layer, Layer)
        self.setText(f"Move layer {layer.name}")
        self.layer_model: LayerModel = layer_model
        self.start: int = start
        self.target: int = target
        if start == target:
            self.setObsolete(True)

    def redo(self) -> None:
        if not self.layer_model.move_item(self.start, self.target, QModelIndex()):
            self.setObsolete(True)

    def undo(self) -> None:
        if self.start < self.target:
            start: int = self.target - 1
            target: int = self.start
        elif self.start > self.target:
            start = self.target
            target = self.start + 1
        else:
            start = self.start
            target = self.start
        self.layer_model.move_item(start, target, QModelIndex())
