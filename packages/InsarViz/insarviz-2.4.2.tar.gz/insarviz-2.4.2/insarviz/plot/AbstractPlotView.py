# -*- coding: utf-8 -*-
""" PlotView

This module contains classes pertaining to the display of data in plot views.
Data selected by the user is displayed in several plots.

Works with the PlotModel module, as in a Model/View architecture.
"""

from typing import Any, Optional, Iterable, Union, overload

import datetime

import pyqtgraph as pg

from pyqtgraph.GraphicsScene import exportDialog

from PySide6.QtCore import (
    Qt, QObject, Signal, Slot, QAbstractProxyModel, QAbstractItemModel, QModelIndex
)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QPushButton

from insarviz.custom_widgets import AnimatedToggle

from insarviz.plot.PlotModel import PlotModel


# PlotWidget classes ###############################################################################

class AbstractPlotWidget(pg.PlotWidget):
    """
    Based on pyqtgraph's GraphicsLayoutWidget
    """

    sigcurveSelected = Signal()

    default_padding = 0.05
    max_padding = 0.15

    # style colors
    DARK_THEME: bool = False
    LIGHT_THEME: bool = True

    def __init__(self, plot_model: PlotModel):
        super().__init__()
        self.plot_model: PlotModel = plot_model
        self.tooltip_text: dict[str, str] = {}
        self.plotItem.setLabel('left', "LOS Displacement")
        self.plotItem.getAxis('left').enableAutoSIPrefix(False)
        self.plotItem.getViewBox().setDefaultPadding(self.default_padding)
        plot_model.loader.data_units_loaded.connect(self.set_data_units)

    @Slot(object, object, object)
    def on_points_hover(self, curve: pg.PlotDataItem, points: list, _) -> None:
        if len(points) == 0:
            if curve.name() in self.tooltip_text:
                del self.tooltip_text[curve.name()]
        else:
            def x_format(x):
                if isinstance(self.plotItem.getAxis('bottom'), pg.DateAxisItem):
                    return datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d')
                return int(x)

            def y_format(y):
                units = f" {self.plot_model.loader.units}"
                if units == ' Undefined units':
                    units = ''
                return f"{y:.3f}{units}"

            self.tooltip_text[curve.name()] = curve.name() + "\n\n" + "\n\n".join(
                [f"x: {x_format(p.pos().x())}\ny: {y_format(p.pos().y())}" for p in points])
        text = "\n\n".join([v for v in self.tooltip_text.values()])
        self.plotItem.getViewBox().setToolTip(text)

    @Slot(str)
    def set_data_units(self, units: str):
        """
        Set the unit string of the Y axis "LOS Displacement {units}"
        """
        self.plotItem.setLabel('left', "LOS Displacement", units=units)

    @Slot(bool)
    def set_style(self, style: bool) -> None:
        """
        Set the plot theme (light or dark). Called when clicking on theme toggle,
        alternate between dark and light.

        Parameters
        ----------
        style : bool
            The state of the toggle, compared to self.DARK_THEME and self.LIGHT_THEME
        """
        (ax1, ax2) = (self.plotItem.getAxis('bottom'), self.plotItem.getAxis('left'))
        if style == self.DARK_THEME:
            # black background
            self.setBackground('k')
            self.plotItem.setTitle(self.plotItem.titleLabel.text, color=.5)
            ax1.setPen('w')
            ax2.setPen('w')
            ax1.setTextPen('w')
            ax2.setTextPen('w')
        elif style == self.LIGHT_THEME:
            # white background
            self.setBackground('w')
            self.plotItem.setTitle(self.plotItem.titleLabel.text, color='k')
            ax1.setPen('k')
            ax2.setPen('k')
            ax1.setTextPen('k')
            ax2.setTextPen('k')
        # update view: for some reason, just 'show' is not enough:
        self.repaint()


# PlotWindow classes ###############################################################################

class AbstractPlotWindow(QWidget):
    """
    Window to display a PlotWidget
    """

    def __init__(self, plot_model: PlotModel, plot_widget: AbstractPlotWidget):
        super().__init__()
        self.plot_model = plot_model
        self.plot_widget: AbstractPlotWidget = plot_widget
        self.plot_widget.set_style(AbstractPlotWidget.LIGHT_THEME)
        # toolbar
        self.toolbar: QToolBar = QToolBar(self)
        self.theme_switch: AnimatedToggle = AnimatedToggle()
        self.theme_switch.setChecked(True)
        self.theme_switch.toggled.connect(self.plot_widget.set_style)
        self.theme_switch.setToolTip('Theme switch (light/dark background)')
        self.toolbar.addWidget(self.theme_switch)
        self.autorange_button: QPushButton = QPushButton("Autorange", self)
        self.autorange_button.setToolTip("Automatically adjust axis range")
        self.autorange_button.clicked.connect(self.autorange)
        self.toolbar.addWidget(self.autorange_button)
        self.export_button: QPushButton = QPushButton("Export...", self)
        self.export_button.clicked.connect(self.export)
        # export dialog
        self.export_dialog = exportDialog.ExportDialog(self.plot_widget.plotItem.scene())
        # layout
        layout = QVBoxLayout()
        layout.setMenuBar(self.toolbar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

    def autorange(self) -> None:
        self.plot_widget.getPlotItem().getViewBox().autoRange()
        self.plot_widget.getPlotItem().autoBtnClicked()

    def export(self) -> None:
        self.export_dialog.show(self.plot_widget.plotItem)

# ProxyNoItemModel class ###########################################################################


class ProxyNoItemModel(QAbstractProxyModel):

    # add a 0th row to a source model, with noitem_text and that can be selected

    def __init__(self, source_model: QAbstractItemModel, noitem_text: str):
        super().__init__()
        self.setSourceModel(source_model)
        self.noitem_string = noitem_text

    # methods reimplemented from QAbstractProxyModel

    def setSourceModel(self, model: QAbstractItemModel) -> None:
        # pylint: disable=missing-function-docstring, invalid-name
        if self.sourceModel() is not None:
            self.sourceModel().rowsAboutToBeInserted.disconnect(self.source_rows_about_inserted)
            self.sourceModel().rowsInserted.disconnect(self.source_rows_inserted)
            self.sourceModel().rowsAboutToBeRemoved.disconnect(self.source_rows_about_removed)
            self.sourceModel().rowsRemoved.disconnect(self.source_rows_removed)
            self.sourceModel().dataChanged.disconnect(self.source_data_changed)
        super().setSourceModel(model)
        self.sourceModel().rowsAboutToBeInserted.connect(self.source_rows_about_inserted)
        self.sourceModel().rowsInserted.connect(self.source_rows_inserted)
        self.sourceModel().rowsAboutToBeRemoved.connect(self.source_rows_about_removed)
        self.sourceModel().rowsRemoved.connect(self.source_rows_removed)
        self.sourceModel().dataChanged.connect(self.source_data_changed)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # pylint: disable=missing-function-docstring, invalid-name
        if parent == QModelIndex():
            return self.sourceModel().rowCount(QModelIndex()) + 1
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        return 1

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        # pylint: disable=missing-function-docstring, invalid-name
        if parent.isValid() or self.rowCount(parent) <= row or self.columnCount(parent) <= column:
            return QModelIndex()
        if row > 0:
            pointer = self.sourceModel().index(row-1, column, QModelIndex()).internalPointer()
        else:
            pointer = None
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
            # no checkbox
            return None
        if index.isValid() and index.row() == 0:
            # Noitem item
            if role == Qt.ItemDataRole.DisplayRole:
                return self.noitem_string
            return None
        return super().data(index, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # pylint: disable=missing-function-docstring
        if index.isValid() and index.row() == 0:
            # Noitem item
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        return super().flags(index)

    def mapFromSource(self, sourceIndex: QModelIndex) -> QModelIndex:
        # pylint: disable=missing-function-docstring, invalid-name
        if not sourceIndex.isValid():
            return QModelIndex()
        return self.index(sourceIndex.row()+1, sourceIndex.column(), QModelIndex())

    def mapToSource(self, proxyIndex: QModelIndex) -> QModelIndex:
        # pylint: disable=missing-function-docstring, invalid-name
        if not proxyIndex.isValid():
            return QModelIndex()
        if proxyIndex.row() == 0:
            return QModelIndex()
        return self.sourceModel().index(proxyIndex.row()-1, proxyIndex.column(), QModelIndex())

    # custom methods

    @Slot(QModelIndex, int, int)
    def source_rows_about_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=missing-function-docstring
        self.beginInsertRows(self.mapFromSource(parent), first + 1, last + 1)

    @Slot(QModelIndex, int, int)
    def source_rows_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=missing-function-docstring, disable=unused-argument
        self.endInsertRows()

    @Slot(QModelIndex, int, int)
    def source_rows_about_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=missing-function-docstring
        self.beginRemoveRows(self.mapFromSource(parent), first + 1, last + 1)

    @Slot(QModelIndex, int, int)
    def source_rows_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        # pylint: disable=unused-argument, missing-function-docstring
        self.endRemoveRows()

    #  TODO cannot find correct Slot signature:
    # @Slot(QModelIndex, QModelIndex, list) not working
    def source_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex,
                            roles: Iterable[int]) -> None:
        # pylint: disable=missing-function-docstring
        self.dataChanged.emit(self.mapFromSource(top_left), self.mapFromSource(bottom_right), roles)
