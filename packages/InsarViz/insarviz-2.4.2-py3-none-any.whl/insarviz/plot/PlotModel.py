#!/usr/bin/env python3
""" PlotModel

This module contains the PlotModel class pertaining to the management of data
selected by the user to be displayed in plot views.

Works with the PlotView module, as in a Model/View architecture.

"""

from typing import Any, Optional, Union, Iterable, overload

import numpy as np

from PySide6.QtCore import (
    Qt, QObject, Slot, Signal, QAbstractProxyModel, QModelIndex, QPersistentModelIndex,
    QAbstractItemModel
)

from insarviz.Loader import Loader

from insarviz.map.layers.LayerModel import LayerModel

from insarviz.map.layers.SelectionLayer import SelectionItem

from insarviz.Roles import Roles


# PlotModel class ##################################################################################

class PlotModel(QObject):

    closed = Signal()
    updated_pointer_info = Signal(tuple, np.ndarray)
    points_added = Signal(int, int)
    points_removed = Signal(int, int)
    points_updated = Signal(int, int, list)
    profiles_added = Signal(int, int)
    profiles_removed = Signal(int, int)
    profiles_updated = Signal(int, int, list)
    references_added = Signal(int, int)
    references_removed = Signal(int, int)
    references_updated = Signal(int, int, list)

    def __init__(self, loader: Loader):
        """
        Model for plots
        get and transform date/band values (timestamps, datetime or int)
        get and prepare data for plots

        Note that band index in data structures start at 0 like in usual python, whereas band index
        start at 1 in MapModel and in gdal, MapModel/gdal indexes are transformed using:
        self.loader.dataset.indexes.index(band_index)

        Parameters
        ----------
        loader : Loader

        Returns
        -------
        None.
        """
        super().__init__()
        self.loader: Loader = loader
        self.loader.data_invalidated.connect(self.on_data_invalidated)
        # data for graphs:
        self.points: ProxySelectionModel = ProxySelectionModel()
        #  list of arrays: points_data[point][date]
        self.points_data: list[np.ndarray] = []
        self.profiles: ProxySelectionModel = ProxySelectionModel()
        # list of arrays profiles_data[profile][point along profile, date]
        self.profiles_data: list[np.ndarray] = []
        self.references: ProxySelectionModel = ProxySelectionModel()
        # list of arrays references_data[reference][date]
        self.references_data: list[np.ndarray] = []
        # signals and slots
        self.points.rowsInserted.connect(lambda _, first, last: self.add_points(first, last))
        self.points.rowsRemoved.connect(lambda _, first, last: self.remove_points(first, last))
        self.points.dataChanged.connect(lambda topLeft, bottomRight, roles:
                                        self.update_points(topLeft.row(), bottomRight.row(), roles))
        self.profiles.rowsInserted.connect(lambda _, first, last: self.add_profiles(first, last))
        self.profiles.rowsRemoved.connect(lambda _, first, last: self.remove_profiles(first, last))
        self.profiles.dataChanged.connect(lambda topLeft, bottomRight, roles: self.update_profiles(
            topLeft.row(), bottomRight.row(), roles))
        self.references.rowsInserted.connect(
            lambda _, first, last: self.add_references(first, last))
        self.references.rowsRemoved.connect(
            lambda _, first, last: self.remove_references(first, last))
        self.references.dataChanged.connect(lambda topLeft, bottomRight, roles:
                                            self.update_references(topLeft.row(), bottomRight.row(),
                                                                   roles))

    def close(self) -> None:
        self.closed.emit()
        self.points.set_root_index()
        self.points_data = []
        self.profiles.set_root_index()
        self.profiles_data = []
        self.references.set_root_index()
        self.references_data = []

    @Slot()
    def on_data_invalidated(self) -> None:
        self.update_points(0, len(self.points_data)-1, [Roles.ComputeDataRole])
        self.update_profiles(0, len(self.profiles_data)-1, [Roles.ComputeDataRole])
        self.update_references(0, len(self.references_data)-1, [Roles.ComputeDataRole])

    # connected to LayerModel.selection_initialized
    @Slot(object)
    def on_selection_init(self, layer_model: LayerModel) -> None:
        assert layer_model.selection is not None
        selection_index = layer_model.index(
            layer_model.selection.child_number(), 0, QModelIndex())
        points_folder_index = layer_model.index(
            layer_model.selection.points_folder.child_number(), 0, selection_index)
        profiles_folder_index = layer_model.index(
            layer_model.selection.profiles_folder.child_number(), 0, selection_index)
        references_folder_index = layer_model.index(
            layer_model.selection.references_folder.child_number(), 0, selection_index)
        self.points.setSourceModel(layer_model)
        self.points.set_root_index(points_folder_index)
        self.profiles.setSourceModel(layer_model)
        self.profiles.set_root_index(profiles_folder_index)
        self.references.setSourceModel(layer_model)
        self.references.set_root_index(references_folder_index)
        if layer_model.rowCount(points_folder_index):
            self.add_points(0, layer_model.rowCount(points_folder_index)-1)
        if layer_model.rowCount(profiles_folder_index):
            self.add_profiles(0, layer_model.rowCount(profiles_folder_index)-1)
        if layer_model.rowCount(references_folder_index):
            self.add_references(0, layer_model.rowCount(references_folder_index)-1)

    @Slot(int, int)
    def add_points(self, first: int, last: int) -> None:
        """
        Slot connected to self.points.rowsInserted, add to self.points_data the data corresponding
        to the rows inserted in self.points. Emits self.points_added signal.

        Parameters
        ----------
        first : int
            index of first point/row added
        last : int
            index of last point/row added
        """
        indexes = [self.points.index(i, 0) for i in range(first, last+1)]
        points = [self.points.get_selection_item(i) for i in indexes]
        self.points_data[first:first] = [self.loader.load_profile_window(*i.get_rect()[0])
                                         for i in points]
        self.points_added.emit(first, last)

    @Slot(int, int)
    def remove_points(self, first: int, last: int) -> None:
        """
        Slot connected to self.points.rowsRemoved, remove from self.points_data the data
        corresponding to the rows removed from self.points. Emits self.points_removed signal.

        Parameters
        ----------
        first : int
            index of first point/row removed
        last : int
            index of last point/row removed
        """
        del self.points_data[first:last+1]
        self.points_removed.emit(first, last)

    @Slot(int, int, list)
    def update_points(self, first: int, last: int, roles: list[int]) -> None:
        """
        Slot connected to self.points.dataChanged, update in self.points_data the data corresponding
        to the points that have been changed in self.points. Emits self.points_updated signal.

        Parameters
        ----------
        first : int
            index of first point/row whose data have been modified
        last : int
            index of last point/row whose data have been modified
        roles : list of int
            list of the ItemDataRoles that have been modified
            see https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum and insarviz.Roles
        """
        if Roles.ComputeDataRole in roles:
            indexes = [self.points.index(i, 0) for i in range(first, last+1)]
            points = [self.points.get_selection_item(i) for i in indexes]
            self.points_data[first:last+1] = [self.loader.load_profile_window(*i.get_rect()[0])
                                              for i in points]
        self.points_updated.emit(first, last, roles)

    @Slot(int, int)
    def add_profiles(self, first: int, last: int) -> None:
        """
        Slot connected to self.profiles.rowsInserted, add to self.profiles_data the data
        corresponding to the rows inserted in self.profiles. Emits self.profiles_added signal.

        Parameters
        ----------
        first : int
            index of first profile/row added
        last : int
            index of last profile/row added
        """
        indexes = [self.profiles.index(i, 0) for i in range(first, last+1)]
        profiles = [self.profiles.get_selection_item(i) for i in indexes]
        self.profiles_data[first:first] = [np.array([self.loader.load_profile_window(*rect)
                                                    for rect in i.get_rect()]) for i in profiles]
        self.profiles_added.emit(first, last)

    @Slot(int, int)
    def remove_profiles(self, first: int, last: int) -> None:
        """
        Slot connected to self.profiles.rowsRemoved, remove from self.profiles_data the data
        corresponding to the rows removed from self.profiles. Emits self.profiles_removed signal.

        Parameters
        ----------
        first : int
            index of first profile/row removed
        last : int
            index of last profile/row removed
        """
        del self.profiles_data[first:last+1]
        self.profiles_removed.emit(first, last)

    @Slot(int, int, list)
    def update_profiles(self, first: int, last: int, roles: list[int]) -> None:
        """
        Slot connected to self.profiles.dataChanged, update in self.profiles_data the data
        corresponding to the profiles that have been changed in self.profiles. Emits
        self.profiles_updated signal.

        Parameters
        ----------
        first : int
            index of first profile/row whose data have been modified
        last : int
            index of last profile/row whose data have been modified
        roles : list of int
            list of the ItemDataRoles that have been modified
            see https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum and insarviz.Roles
        """
        if Roles.ComputeDataRole in roles:
            indexes = [self.profiles.index(i, 0) for i in range(first, last+1)]
            profiles = [self.profiles.get_selection_item(i) for i in indexes]
            self.profiles_data[first:last+1] = [np.array([self.loader.load_profile_window(*rect)
                                                for rect in i.get_rect()]) for i in profiles]
        self.profiles_updated.emit(first, last, roles)

    @Slot(int, int)
    def add_references(self, first: int, last: int) -> None:
        """
        Slot connected to self.references.rowsInserted, add to self.references_data the data
        corresponding to the rows inserted in self.references. Emits self.references_added signal.

        Parameters
        ----------
        first : int
            index of first reference/row added
        last : int
            index of last reference/row added
        """
        indexes = [self.references.index(i, 0) for i in range(first, last+1)]
        references = [self.references.get_selection_item(i) for i in indexes]
        self.references_data[first:first] = [self.loader.load_profile_window(*i.get_rect()[0])
                                             for i in references]
        self.references_added.emit(first, last)

    @Slot(int, int)
    def remove_references(self, first: int, last: int) -> None:
        """
        Slot connected to self.references.rowsRemoved, remove from self.references_data the data
        corresponding to the rows removed from self.references. Emits self.references_removed
        signal.

        Parameters
        ----------
        first : int
            index of first reference/row removed
        last : int
            index of last reference/row removed
        """
        del self.references_data[first:last+1]
        self.references_removed.emit(first, last)

    @Slot(int, int, list)
    def update_references(self, first: int, last: int, roles: list[int]) -> None:
        """
        Slot connected to self.references.dataChanged, update in self.references_data the data
        corresponding to the points that have been changed in self.references. Emits
        self.references_updated signal.

        Parameters
        ----------
        first : int
            index of first reference/row whose data have been modified
        last : int
            index of last reference/row whose data have been modified
        roles : list of int
            list of the ItemDataRoles that have been modified
            see https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum and insarviz.Roles
        """
        if Roles.ComputeDataRole in roles:
            indexes = [self.references.index(i, 0) for i in range(first, last+1)]
            references = [self.references.get_selection_item(i) for i in indexes]
            self.references_data[first:first] = [self.loader.load_profile_window(*i.get_rect()[0])
                                                 for i in references]
        self.references_updated.emit(first, last, roles)

    @Slot(tuple, int)
    def update_pointer(self, pos: tuple, date_index: Optional[int]) -> None:
        """
        load current pointer data (for plots)
        launched by mouseMoveEvent on MapView
        date_index correspond to MapModel.current_band_index (starting from 1 like in gdal)
        """
        if pos == ():
            self.updated_pointer_info.emit((), np.array([]))
        else:
            assert self.loader.dataset is not None
            assert date_index is not None and date_index in self.loader.dataset.indexes
            # then pos = (i,j)
            (i, j) = pos
            # load data for all dates at current pointer's position
            pointer_data = self.loader.load_profile_window(i, j)
            # emit (x, y, date, value)
            # need to take date_index-1 because date_index starts from 1 like in gdal
            self.updated_pointer_info.emit(
                (i, j, self.loader.dates[date_index-1], pointer_data[date_index-1]), pointer_data)


# ProxySelectionModel class ########################################################################

class ProxySelectionModel(QAbstractProxyModel):

    # transform a TreeModel into a list of root_index's children
    # (children at depth >1 are filtered out)
    # return the list of the selection items in a folder when used with root_index=SelectionFolder
    # also replace Qt.CheckStateRole by SelectionItem.ShowCurveRole

    def __init__(self, source_model: Optional[QAbstractItemModel] = None,
                 root_index: Optional[QModelIndex] = None):
        super().__init__()
        if source_model is not None:
            self.setSourceModel(source_model)
        self.root_index: Optional[QPersistentModelIndex]
        self.set_root_index(root_index)

    # methods reimplemented from QAbstractProxyModel

    def setSourceModel(self, source_model: QAbstractItemModel) -> None:
        # pylint: disable=missing-function-docstring, invalid-name
        if self.sourceModel() is not None:
            self.sourceModel().rowsAboutToBeInserted.disconnect(self.source_rows_about_inserted)
            self.sourceModel().rowsInserted.disconnect(self.source_rows_inserted)
            self.sourceModel().rowsAboutToBeRemoved.disconnect(self.source_rows_about_removed)
            self.sourceModel().rowsRemoved.disconnect(self.source_rows_removed)
            self.sourceModel().dataChanged.disconnect(self.source_data_changed)
            self.sourceModel().modelReset.disconnect(self.set_root_index)
        super().setSourceModel(source_model)
        self.sourceModel().rowsAboutToBeInserted.connect(self.source_rows_about_inserted)
        self.sourceModel().rowsInserted.connect(self.source_rows_inserted)
        self.sourceModel().rowsAboutToBeRemoved.connect(self.source_rows_about_removed)
        self.sourceModel().rowsRemoved.connect(self.source_rows_removed)
        self.sourceModel().dataChanged.connect(self.source_data_changed)
        self.sourceModel().modelReset.connect(self.set_root_index)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # pylint: disable=missing-function-docstring, invalid-name
        if parent == QModelIndex():
            if self.root_index is None or not self.root_index.isValid():
                return 0
            return self.sourceModel().rowCount(QModelIndex(self.root_index))
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        return 1

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        # pylint: disable=missing-function-docstring
        if parent.isValid() or self.rowCount(parent) <= row or self.columnCount(parent) <= column:
            return QModelIndex()
        assert self.root_index is not None and self.root_index.isValid()
        pointer = self.sourceModel().index(row, column,
                                           QModelIndex(self.root_index)).internalPointer()
        return self.createIndex(row, column, pointer)

    # see https://mypy.readthedocs.io/en/stable/more_types.html#function-overloading
    @overload
    def parent(self, child: QModelIndex) -> QModelIndex: ...

    @overload
    def parent(self) -> QObject: ...

    def parent(self, child: Optional[QModelIndex] = None) -> Union[QObject, QModelIndex]:
        # pylint: disable=missing-function-docstring
        if child is None:
            return super().parent()
        return QModelIndex()

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        # pylint: disable=missing-function-docstring
        if role == Qt.ItemDataRole.CheckStateRole:
            # use SelectionItem.show_curve field
            return super().data(index, SelectionItem.ShowCurveRole)
        return super().data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        # pylint: disable=missing-function-docstring, invalid-name
        if role == Qt.ItemDataRole.CheckStateRole:
            # use SelectionItem.show_curve field
            return super().setData(index, value, SelectionItem.ShowCurveRole)
        if role in (Roles.ProfileTemporalRole, Roles.ProfileSpatialRole):
            return super().setData(index, value, role)
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # pylint: disable=missing-function-docstring
        return super().flags(index) & (~Qt.ItemFlag.ItemIsEditable)  # remove editable flag

    def mapFromSource(self, sourceIndex: QModelIndex) -> QModelIndex:
        # pylint: disable=missing-function-docstring, invalid-name
        if not sourceIndex.isValid():
            return QModelIndex()
        if sourceIndex == self.root_index:
            return QModelIndex()
        if sourceIndex.parent() == self.root_index:
            return self.index(sourceIndex.row(), sourceIndex.column(), QModelIndex())
        return QModelIndex()

    def mapToSource(self, proxyIndex: QModelIndex) -> QModelIndex:
        # pylint: disable=missing-function-docstring, invalid-name
        if self.root_index is None or not self.root_index.isValid():
            return QModelIndex()
        if not proxyIndex.isValid():
            return QModelIndex(self.root_index)
        return self.sourceModel().index(proxyIndex.row(), proxyIndex.column(),
                                        QModelIndex(self.root_index))

    # custom methods
    @Slot()
    def set_root_index(self, index: Optional[QModelIndex] = None) -> None:
        if index is None:
            self.root_index = None
        else:
            self.root_index = QPersistentModelIndex(index)

    def get_selection_item(self, index: QModelIndex) -> SelectionItem:
        layer_model = self.sourceModel()
        assert isinstance(layer_model, LayerModel)
        item = layer_model.get_item(index)
        assert isinstance(item, SelectionItem)
        return item

    @Slot(QModelIndex, int, int)
    def source_rows_about_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=missing-function-docstring
        if parent == self.root_index:
            self.beginInsertRows(self.mapFromSource(parent), first, last)

    @Slot(QModelIndex, int, int)
    def source_rows_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=missing-function-docstring, unused-argument
        if parent == self.root_index:
            self.endInsertRows()

    @Slot(QModelIndex, int, int)
    def source_rows_about_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=missing-function-docstring
        if parent == self.root_index:
            self.beginRemoveRows(self.mapFromSource(parent), first, last)

    @Slot(QModelIndex, int, int)
    def source_rows_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=unused-argument, missing-function-docstring
        if parent == self.root_index:
            self.endRemoveRows()

    #  TODO cannot find correct Slot signature:
    # @Slot(QModelIndex, QModelIndex, list) not working
    def source_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex,
                            roles: Iterable[int]) -> None:
        # pylint: disable=missing-function-docstring
        if top_left.parent() == self.root_index and bottom_right.parent() == self.root_index:
            if top_left.column() == bottom_right.column() == 0:
                self.dataChanged.emit(self.mapFromSource(top_left),
                                      self.mapFromSource(bottom_right), roles)

    @Slot()
    def show_all_curves(self) -> None:
        for i in range(self.rowCount(QModelIndex())):
            index = self.index(i, 0, QModelIndex())
            self.setData(index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)

    @Slot()
    def hide_all_curves(self) -> None:
        for i in range(self.rowCount(QModelIndex())):
            index = self.index(i, 0, QModelIndex())
            self.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
