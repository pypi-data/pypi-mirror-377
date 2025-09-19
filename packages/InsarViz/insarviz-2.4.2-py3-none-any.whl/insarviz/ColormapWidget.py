# -*- coding: utf-8 -*-

""" PaletteView

This module handles the creation of the Palette view: an interactive plot
of the distribution of data values and its corresponding color scheme
Also handles user interactions with it (change color gradient and its
correspondance with data values)

Contains class:
    * Palette
"""

# imports ##########################################################################################

from typing import Optional

import logging

import numpy as np

from PySide6.QtCore import Qt, Signal, Slot, QSize, QEvent

from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QPushButton

from PySide6.QtGui import QResizeEvent, QColor

from pyqtgraph import HistogramLUTWidget, BarGraphItem, LegendItem, GraphicsView
from pyqtgraph.widgets.ColorMapMenu import ColorMapMenu, buildMenuEntryAction, PrivateActionData

from pyqtgraph.colormap import ColorMap

from insarviz.colormaps import my_colormaps, my_cyclic_colormaps

from insarviz.custom_widgets import QtWaitingSpinner


logger = logging.getLogger(__name__)


# ColormapWidget class #############################################################################

class ColormapWidget(QWidget):

    autorange_threshold = 0.02
    default_padding = 0.15
    max_padding = 0.4

    # connected to MapModel.set_v0_v1
    v0_v1_changed = Signal(float, float)
    # connected to MapModel.set_colormap
    colormap_changed = Signal(ColorMap)
    #
    compute_histograms = Signal(tuple)
    cancel_compute_histograms = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self.histogram_widget = myHistogramWidget(self)
        # add a curve for total histogram
        self.total_hist_plot = BarGraphItem(x0=[], x1=[], y0=[], y1=[],
                                            pen=None, brush=(20, 20, 220, 100))
        self.total_hist_plot.setZValue(10)
        self.total_hist_plot.setRotation(90)
        self.histogram_widget.vb.addItem(self.total_hist_plot)
        # add a curve for band histogram
        # (total data histogram use the base HistogramLUTWidget mono curve: self.plot)
        self.band_hist_plot = BarGraphItem(x0=[], x1=[], y0=[], y1=[],
                                           pen=None, brush=(220, 20, 20, 100))
        self.band_hist_plot.setZValue(10)
        self.band_hist_plot.setRotation(90)
        self.histogram_widget.vb.addItem(self.band_hist_plot)
        # legend
        self.legend = LegendItem()
        self.legend.addItem(self.total_hist_plot, "all bands")
        self.legend.addItem(self.band_hist_plot, "current band")
        self.legend_widget = myLegendWidget(parent=parent)
        self.legend_widget.setCentralWidget(self.legend)
        # toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.autorange_total_button: QPushButton = QPushButton("Autorange all bands", self)
        self.autorange_total_button.setToolTip("Automatically adjust the colormap mapping using the"
                                               " all band histogram")
        self.autorange_total_button.clicked.connect(self.autorange_total)
        self.toolbar.addWidget(self.autorange_total_button)
        self.autorange_band_button: QPushButton = QPushButton("Autorange current band", self)
        self.autorange_band_button.setToolTip("Automatically adjust the colormap mapping using the"
                                              " current band histogram")
        self.autorange_band_button.clicked.connect(self.autorange_band)
        self.toolbar.addWidget(self.autorange_band_button)
        self.compute_histogram_button: QPushButton = QPushButton("Recompute histograms", self)
        self.compute_histogram_button.setToolTip(
            "Recompute the histograms using the area to define outliers")
        self.compute_histogram_button.clicked.connect(self.request_histograms)
        self.compute_action = self.toolbar.addWidget(self.compute_histogram_button)
        self.cancel_button: QPushButton = QPushButton("Cancel", self)
        self.cancel_button.setToolTip("Cancel histogram computation")
        self.cancel_button.clicked.connect(self.cancel_compute_histograms)
        self.cancel_action = self.toolbar.addWidget(self.cancel_button)
        # layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.histogram_widget, stretch=1)
        self.main_layout.addWidget(self.legend_widget)
        self.setLayout(self.main_layout)
        # internal signal and slots
        self.histogram_widget.sigLevelsChanged.connect(
            lambda _: self.v0_v1_changed.emit(*self.histogram_widget.getLevels()))
        self.histogram_widget.gradient.menu.sigColorMapTriggered.connect(
            self.colormap_changed.emit)
        # set disabled
        self.setDisabled(True)
        self.cancel_action.setVisible(False)
        self.spinner = QtWaitingSpinner(self.histogram_widget)

    @Slot()
    def on_compute_histogram(self) -> None:
        self.histogram_widget.setDisabled(True)
        self.legend_widget.setDisabled(True)
        self.autorange_total_button.setDisabled(True)
        self.autorange_band_button.setDisabled(True)
        self.compute_histogram_button.setDisabled(True)
        if not len(self.total_hist_plot.opts.get('x0')) == 0:
            self.compute_action.setVisible(False)
            self.cancel_action.setVisible(True)
        self.spinner.start()

    @Slot()
    def request_histograms(self) -> None:
        self.compute_histograms.emit(self.histogram_widget.getLevels())

    @Slot()
    def on_histograms_computed(self) -> None:
        self.setEnabled(True)
        self.histogram_widget.setEnabled(True)
        self.legend_widget.setEnabled(True)
        self.autorange_total_button.setEnabled(True)
        self.autorange_band_button.setEnabled(True)
        self.compute_histogram_button.setEnabled(True)
        self.compute_action.setVisible(True)
        self.cancel_action.setVisible(False)
        self.spinner.stop()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        width = 0.85*self.histogram_widget.size().width()
        self.spinner.setInnerRadius(4*width//20)
        self.spinner.setLineLength(6*width//20)
        self.spinner.setLineWidth(max(2, (2*width)//20))

    def sizeHint(self) -> QSize:
        return QSize(self.minimumWidth(), self.minimumHeight())

    def on_close(self) -> None:
        self.set_total_histogram(np.array([]), np.array([]))
        self.set_band_histogram(np.array([]), np.array([]))
        self.set_default_colormap()
        self.setDisabled(True)

    @Slot(np.ndarray, np.ndarray)
    def set_total_histogram(self, hist: np.ndarray, bins: np.ndarray) -> None:
        self.total_hist_plot.setOpts(x0=bins[:-1], x1=bins[1:], y0=np.zeros(len(hist)), y1=hist)
        if len(hist) == 0:
            return
        self.autorange_total()
        self.histogram_widget.vb.setYRange(bins[1], bins[-2], padding=self.default_padding)
        ymin = float(bins[0] - (bins[-1] - bins[0]) * self.max_padding)
        ymax = float(bins[-1] + (bins[-1] - bins[0]) * self.max_padding)
        self.histogram_widget.vb.setLimits(yMin=ymin, yMax=ymax)

    @Slot(np.ndarray, np.ndarray)
    def set_band_histogram(self, hist: np.ndarray, bins: np.ndarray) -> None:
        self.band_hist_plot.setOpts(x0=bins[:-1], x1=bins[1:], y0=np.zeros(len(hist)), y1=hist)

    def autorange_from_hist(self, hist: np.ndarray, bins: np.ndarray) -> tuple[float, float]:
        assert len(hist) > 2 and len(hist)+1 == len(bins)
        # get the first index where the histogram cumulative sum is greater than threshold
        idx_v0 = np.where(np.cumsum(hist) > self.autorange_threshold)[0][0]
        # take the maximum between this index and 1 to skip the left outlier bin
        idx_v0 = np.max((1, idx_v0))
        # get the left boundary of this bin (hence the [:-1] to get the left boundaries)
        v0 = bins[:-1][idx_v0]
        # get the last index where the histogram backward cumulative sum is greater than threshold
        # (backward hence hist[::-1], and to get the correct index in the backward cumulative sum
        # has to be inversed again hence the second [::-1])
        idx_v1 = np.where(np.cumsum(hist[::-1])[::-1] > self.autorange_threshold)[0][-1]
        # take the minimum between this index and the len -2 to skip the right outlier bin
        idx_v1 = np.min((len(hist) - 2, idx_v1))
        # get the right boundary of this bin (hence the [1:] to get the right boundaries)
        v1 = bins[1:][idx_v1]
        return (v0, v1)

    @Slot()
    def autorange_total(self) -> None:
        hist = self.total_hist_plot.opts.get('y1')
        if len(hist) == 0:
            return
        bins = np.empty(len(hist)+1)
        bins[:-1] = self.total_hist_plot.opts.get('x0')
        bins[-1] = self.total_hist_plot.opts.get('x1')[-1]
        v0, v1 = self.autorange_from_hist(hist, bins)
        self.histogram_widget.setLevels(v0, v1)

    @Slot()
    def autorange_band(self) -> None:
        hist = self.band_hist_plot.opts.get('y1')
        if len(hist) == 0:
            return
        bins = np.empty(len(hist)+1)
        bins[:-1] = self.band_hist_plot.opts.get('x0')
        bins[-1] = self.band_hist_plot.opts.get('x1')[-1]
        v0, v1 = self.autorange_from_hist(hist, bins)
        self.histogram_widget.setLevels(v0, v1)

    # connected to Loader.data_units_loaded
    @Slot(str)
    def set_data_units(self, units: str) -> None:
        self.histogram_widget.axis.setLabel("LOS Displacement", units=units)

    @Slot(float, float)
    def set_v0_v1(self, v0: float, v1: float) -> None:
        self.histogram_widget.setLevels(v0, v1)

    def set_default_colormap(self) -> None:
        # greyscale is the first colormap action (see colormaps.py)
        self.histogram_widget.gradient.menu.actions()[0].trigger()

    @Slot(str)
    def set_colormap(self, name: str) -> None:
        for action in self.histogram_widget.gradient.menu.actions():
            if action.menu():
                for sub_action in action.menu().actions():
                    if isinstance(sub_action.data(), PrivateActionData):
                        if self.histogram_widget.gradient.menu.actionDataToColorMap(sub_action.data()).name == name:
                            sub_action.trigger()
                            return
            elif isinstance(action.data(), PrivateActionData):
                if self.histogram_widget.gradient.menu.actionDataToColorMap(action.data()).name == name:
                    action.trigger()
                    return
        logger.warning(f"colormap {name} not found, switch to greyscale")
        self.set_default_colormap()


class myHistogramWidget(HistogramLUTWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent, levelMode='mono', gradientPosition='right',
                         orientation='vertical')
        # remove the default gradient menu of pyqtgraph.GradientEditorItem
        del self.gradient.menu
        # create custom gradient menu with chosen default colormaps + our owns
        self.gradient.menu = ColorMapMenu(userList=my_colormaps)
        # remove the None action (that selects a greyscale colormap)
        self.gradient.menu.removeAction(self.gradient.menu.actions()[0])
        # add cyclic colormaps submenu
        cyclic_submenu = self.gradient.menu.addMenu("cyclic")
        for cmap in my_cyclic_colormaps:
            buildMenuEntryAction(cyclic_submenu, cmap.name, cmap)
        # connect gradient menu action as in pyqtgraph.GradientEditorItem
        self.gradient.menu.sigColorMapTriggered.connect(self.gradient.colorMapMenuClicked)
        # remove the ticks of gradient
        self.gradient.showTicks(False)
        # set minimum width so that colorbar is not hidden when minimized
        self.setMinimumWidth(115)
        self.setMaximumWidth(250)
        # move the region indicator to background
        self.region.setZValue(-1)
        # remove the default histogram curve
        self.vb.removeItem(self.plot)

    def changeEvent(self, event: QEvent):
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            if self.isEnabled():
                self.setForegroundBrush(Qt.GlobalColor.transparent)
            else:
                self.setForegroundBrush(QColor(128, 128, 128, 80))


class myLegendWidget(GraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def changeEvent(self, event: QEvent):
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            if self.isEnabled():
                self.setForegroundBrush(Qt.GlobalColor.transparent)
            else:
                self.setForegroundBrush(QColor(128, 128, 128, 80))
