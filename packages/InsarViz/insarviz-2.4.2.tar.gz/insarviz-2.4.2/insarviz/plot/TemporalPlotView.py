# -*- coding: utf-8 -*-

from typing import Union

import warnings

import numpy as np

import pyqtgraph as pg

from PySide6.QtCore import Qt, Slot, Signal, QModelIndex, QPointF

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QListView, QAbstractItemView, QSplitter, QToolBar, QLabel,
    QSlider, QVBoxLayout, QHBoxLayout, QWidget, QSpinBox, QSizePolicy
)

from PySide6.QtGui import QIcon, QAction, QGuiApplication

from insarviz.BandSlider import SliderLeftClickStyle

from insarviz.plot.AbstractPlotView import AbstractPlotWindow, AbstractPlotWidget, ProxyNoItemModel

from insarviz.plot.PlotModel import PlotModel

from insarviz.Loader import Loader

from insarviz.map.layers.SelectionLayer import SelectionItem

from insarviz.utils import get_nearest

from insarviz.Roles import Roles

from insarviz.BandSlider import TimelineHandle


# TemporalPlotWidget class #########################################################################

class TemporalPlotWidget(AbstractPlotWidget):
    """
    temporal evolution plot
    """

    def __init__(self, plot_model: PlotModel):
        super().__init__(plot_model)
        # used by insarviz.exporters.myCSVExporter
        self.plotItem.insarviz_widget = self
        # date marker synchronized with application's window slider
        self.date_marker: DateMarker = DateMarker(self.plot_model.loader)
        # pointer curve
        self.pointer_curve: pg.PlotDataItem = pg.PlotDataItem(symbol='o', symbolSize=5,
                                                              antialias=True)
        self.pointer_curve.setPen("r", width=2)
        self.pointer_curve.setSymbolPen(None)
        self.pointer_curve.setSymbolBrush("r")
        self.pointer_curve.opts["name"] = "pointer"
        self.pointer_curve.setZValue(1.)  # interactive curve is plotted in foreground
        # selection items curves
        self.points_curves: list[pg.PlotDataItem] = []
        self.profile_curve: pg.PlotDataItem = pg.PlotDataItem(symbol='o', symbolSize=5,
                                                              antialias=True)
        self.profile_curve.sigPointsHovered.connect(self.on_points_hover)
        self.profile_curve.scatter.setData(hoverable=True, tip=None, hoverBrush='r', hoverSize=8)
        self.profile_curve.setSymbolPen(None)
        self.references_curves: list[pg.PlotDataItem] = []
        self.profile: int = -1  # index of the current profile, -1 means no profile
        self.profile_point: int = 0  # index of the current profile point, 0 means start of the profile
        self.reference: int = -1  # index of the current reference, -1 means no reference
        # signals and slots
        plot_model.loader.data_loaded.connect(self.on_data_loaded)
        plot_model.loader.histograms_computed.connect(self.on_histograms_computed)
        plot_model.closed.connect(self.on_close)
        plot_model.updated_pointer_info.connect(self.plot_pointer_data)
        plot_model.points_added.connect(self.add_points_curves)
        plot_model.points_removed.connect(self.remove_points_curves)
        plot_model.points_updated.connect(self.update_points_curves)
        plot_model.profiles_updated.connect(self.update_profiles_curves)
        plot_model.references_added.connect(self.add_references_curves)
        plot_model.references_removed.connect(self.remove_references_curves)
        plot_model.references_updated.connect(self.update_references_curves)

    @Slot(int)
    def on_data_loaded(self, band_index: int) -> None:
        assert self.plot_model.loader.timestamps is not None
        # x-axis:
        if isinstance(self.plot_model.loader.dates[0], int):
            # dates not available: regular x-axis
            self.plotItem.setAxisItems({'bottom': pg.AxisItem('bottom', text="Band #")})
        else:
            # dates available: x-axis is a TimeAxisItem
            self.plotItem.setAxisItems({'bottom': TimeAxisItem(text='Date', units='yyyy-mm-dd')})
        self.plotItem.setXRange(self.plot_model.loader.timestamps[0],
                                self.plot_model.loader.timestamps[-1], padding=self.default_padding)
        # set the min max range of the x axis
        timedelta = self.plot_model.loader.timestamps[-1] - self.plot_model.loader.timestamps[0]
        xmin = self.plot_model.loader.timestamps[0] - self.max_padding*timedelta
        xmax = self.plot_model.loader.timestamps[-1] + self.max_padding*timedelta
        self.plotItem.setLimits(xMin=xmin, xMax=xmax)
        # date marker
        assert self.plot_model.loader.dataset is not None
        assert band_index in self.plot_model.loader.dataset.indexes
        index = self.plot_model.loader.dataset.indexes.index(band_index)
        self.date_marker.setPos(self.plot_model.loader.timestamps[index])
        self.plotItem.addItem(self.date_marker)
        # pointer curve
        self.plotItem.addItem(self.pointer_curve)

    @Slot()
    def on_histograms_computed(self) -> None:
        assert self.plot_model.loader.total_histogram is not None
        total_bins = self.plot_model.loader.total_histogram[1]
        ydelta = total_bins[-1] - total_bins[0]
        ymin = total_bins[0] - self.max_padding * ydelta
        ymax = total_bins[-1] + self.max_padding * ydelta
        self.plotItem.setLimits(yMin=ymin, yMax=ymax)

    @Slot()
    def on_close(self) -> None:
        self.plotItem.clear()
        del self.points_curves[:]
        #  self.profile_curve is cleared by TemporalPlotWidget.on_close calls
        del self.references_curves[:]
        self.pointer_curve.setData()
        self.pointer_curve.opts["name"] = "pointer"
        self.tooltip_text = {}
        self.plotItem.getViewBox().setToolTip("")

    @Slot(tuple, np.ndarray)
    def plot_pointer_data(self, info: tuple, data: np.ndarray) -> None:
        """
        set pointer curve data from the pixel hovered over on the map
        """
        if info == ():
            self.pointer_curve.setData()
            self.pointer_curve.opts["name"] = "pointer"
        else:
            # test if at least one element of data is not nan
            if not all(np.isnan(data)):
                self.compute_curve(data, self.pointer_curve)
            else:
                self.pointer_curve.setData()
            self.pointer_curve.opts["name"] = f"pointer at ({info[0]}, {info[1]})"

    @Slot(int, int)
    def add_points_curves(self, first: int, last: int) -> None:
        new_curves: list[pg.PlotDataItem] = []
        for i in range(first, last+1):
            point_index: QModelIndex = self.plot_model.points.index(i, 0)
            color = self.plot_model.points.data(point_index, Qt.ItemDataRole.DecorationRole)
            curve: pg.PlotDataItem = pg.PlotDataItem(symbol='o', symbolSize=5, antialias=True)
            curve.sigPointsHovered.connect(self.on_points_hover)
            curve.scatter.setData(hoverable=True, tip=None, hoverBrush='r', hoverSize=8)
            curve.setPen(color, width=2)
            curve.setSymbolPen(None)
            curve.setSymbolBrush(color)
            curve.opts["name"] = self.plot_model.points.data(point_index,
                                                             Qt.ItemDataRole.DisplayRole)
            self.compute_curve(self.plot_model.points_data[i], curve)
            if self.plot_model.points.data(point_index, SelectionItem.ShowCurveRole):
                self.plotItem.addItem(curve)
            new_curves.append(curve)
        self.points_curves[first:first] = new_curves

    @Slot(int, int)
    def remove_points_curves(self, first: int, last: int) -> None:
        for i in range(first, last+1):
            self.plotItem.removeItem(self.points_curves[i])
            # remove tooltip for this curve
            self.points_curves[i].sigPointsHovered.emit(self.points_curves[i], [], None)
        del self.points_curves[first:last+1]

    @Slot(int, int, list)
    def update_points_curves(self, first: int, last: int, roles: list[int]) -> None:
        for i in range(first, last+1):
            point_index = self.plot_model.points.index(i, 0)
            if Roles.ComputeDataRole in roles:
                self.compute_curve(self.plot_model.points_data[i], self.points_curves[i])
                # remove tooltip for this curve
                self.points_curves[i].sigPointsHovered.emit(self.points_curves[i], [], None)
            if Roles.CurveColorRole in roles:
                color = self.plot_model.points.data(point_index, Qt.ItemDataRole.DecorationRole)
                self.points_curves[i].setPen(color, width=2)
                self.points_curves[i].setSymbolPen(None)
                self.points_curves[i].setSymbolBrush(color)
            if Qt.ItemDataRole.EditRole in roles:
                # remove tooltip for this curve
                self.points_curves[i].sigPointsHovered.emit(self.points_curves[i], [], None)
                name = self.plot_model.points.data(point_index, Qt.ItemDataRole.DisplayRole)
                self.points_curves[i].opts["name"] = name
            if SelectionItem.ShowCurveRole in roles:
                show = (self.plot_model.points.data(point_index, SelectionItem.ShowCurveRole) ==
                        Qt.CheckState.Checked)
                if show:
                    with warnings.catch_warnings():
                        # ignore UserWarning for curve already plotted
                        warnings.filterwarnings("ignore", category=UserWarning,
                                                message="Item already added to PlotItem")
                        self.plotItem.addItem(self.points_curves[i])
                else:
                    self.plotItem.removeItem(self.points_curves[i])
                    # remove tooltip for this curve
                    self.points_curves[i].sigPointsHovered.emit(self.points_curves[i], [], None)

    @Slot(int, int, list)
    def update_profiles_curves(self, first: int, last: int, roles: list[int]) -> None:
        if first <= self.profile <= last:
            profile_index = self.plot_model.profiles.index(self.profile, 0)
            if Roles.ComputeDataRole in roles:
                self.compute_curve(
                    self.plot_model.profiles_data[self.profile][self.profile_point, :],
                    self.profile_curve)
                # remove tooltip for this curve
                self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)
            if Roles.CurveColorRole in roles:
                color = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DecorationRole)
                self.profile_curve.setPen(color, width=2)
                self.profile_curve.setSymbolBrush(color)
            if Qt.ItemDataRole.EditRole in roles:
                # remove tooltip for this curve
                self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)
                name = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DisplayRole)
                self.profile_curve.opts["name"] = name

    @Slot(int, int)
    def add_references_curves(self, first: int, last: int) -> None:
        new_curves = []
        for i in range(first, last+1):
            reference_index = self.plot_model.references.index(i, 0)
            color = self.plot_model.references.data(reference_index, Qt.ItemDataRole.DecorationRole)
            curve = pg.PlotDataItem(symbol='o', symbolSize=5, antialias=True)
            curve.sigPointsHovered.connect(self.on_points_hover)
            curve.scatter.setData(hoverable=True, tip=None, hoverBrush='r', hoverSize=8)
            curve.setPen(color, width=2)
            curve.setSymbolPen(None)
            curve.setSymbolBrush(color)
            curve.setZValue(-1.)  # reference curves are plotted in background
            curve.opts["name"] = self.plot_model.references.data(reference_index,
                                                                 Qt.ItemDataRole.DisplayRole)
            self.compute_curve(self.plot_model.references_data[i], curve)
            if self.plot_model.references.data(reference_index, SelectionItem.ShowCurveRole):
                self.plotItem.addItem(curve)
            new_curves.append(curve)
        self.references_curves[first:first] = new_curves

    @Slot(int, int)
    def remove_references_curves(self, first: int, last: int) -> None:
        for i in range(first, last+1):
            self.plotItem.removeItem(self.references_curves[i])
            # remove tooltip for this curve
            self.references_curves[i].sigPointsHovered.emit(self.references_curves[i], [], None)
        del self.references_curves[first:last+1]

    @Slot(int, int, list)
    def update_references_curves(self, first: int, last: int, roles: list[int]) -> None:
        for i in range(first, last+1):
            reference_index = self.plot_model.references.index(i, 0)
            if Roles.ComputeDataRole in roles:
                self.compute_curve(self.plot_model.references_data[i], self.references_curves[i])
                # remove tooltip for this curve
                self.references_curves[i].sigPointsHovered.emit(self.references_curves[i], [], None)
            if Roles.CurveColorRole in roles:
                color = self.plot_model.references.data(reference_index,
                                                        Qt.ItemDataRole.DecorationRole)
                self.references_curves[i].setPen(color, width=2)
                self.references_curves[i].setSymbolPen(None)
                self.references_curves[i].setSymbolBrush(color)
            if Qt.ItemDataRole.EditRole in roles:
                # remove tooltip for this curve
                self.references_curves[i].sigPointsHovered.emit(self.references_curves[i], [], None)
                name = self.plot_model.references.data(reference_index, Qt.ItemDataRole.DisplayRole)
                self.references_curves[i].opts["name"] = name
            if SelectionItem.ShowCurveRole in roles:
                show = (self.plot_model.references.data(reference_index, SelectionItem.ShowCurveRole)
                        == Qt.CheckState.Checked)
                if show:
                    with warnings.catch_warnings():
                        # ignore UserWarning for curve already plotted
                        warnings.filterwarnings("ignore", category=UserWarning,
                                                message="Item already added to PlotItem")
                        self.plotItem.addItem(self.references_curves[i])
                else:
                    self.plotItem.removeItem(self.references_curves[i])
                    # remove tooltip for this curve
                    self.references_curves[i].sigPointsHovered.emit(
                        self.references_curves[i], [], None)

    @Slot(int)
    def change_profile(self, i: int) -> None:
        if self.profile != i:
            # remove tooltip for this curve
            self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)
            if self.profile != -1:
                profile_index = self.plot_model.profiles.index(self.profile, 0)
                self.plot_model.profiles.setData(profile_index, None,
                                                 Roles.ProfileTemporalRole)
        self.profile = i
        if self.profile != -1:
            profile_index = self.plot_model.profiles.index(self.profile, 0)
            color = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DecorationRole)
            self.profile_curve.setPen(color, width=2)
            self.profile_curve.setSymbolBrush(color)
            name = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DisplayRole)
            self.profile_curve.opts["name"] = f"{name} at pixel {self.profile_point}"
            self.compute_curve(self.plot_model.profiles_data[self.profile][self.profile_point, :],
                               self.profile_curve)
            self.plotItem.addItem(self.profile_curve)
        else:
            self.profile_curve.opts["name"] = "no profile"
            self.plotItem.removeItem(self.profile_curve)

    @Slot(int)
    def change_profile_point(self, i: int) -> None:
        self.profile_point = i
        if self.profile != -1:
            profile_index = self.plot_model.profiles.index(self.profile, 0)
            self.plot_model.profiles.setData(profile_index, self.profile_point,
                                             Roles.ProfileTemporalRole)
            name = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DisplayRole)
            self.profile_curve.opts["name"] = f"{name} at pixel {self.profile_point}"
            self.compute_curve(self.plot_model.profiles_data[self.profile][self.profile_point, :],
                               self.profile_curve)

    @Slot(int)
    def change_reference(self, i: int) -> None:
        old_reference: Union[int, np.ndarray]
        if self.reference != -1:
            old_reference = self.plot_model.references_data[self.reference]
        else:
            old_reference = 0
        self.reference = i
        # pointer curve
        if self.pointer_curve.getData() != (None, None):
            self.compute_curve(self.pointer_curve.getData()[1] - old_reference, self.pointer_curve)
        # points
        for k, point_curve in enumerate(self.points_curves):
            self.compute_curve(self.plot_model.points_data[k], point_curve)
        # references
        for k, ref_curve in enumerate(self.references_curves):
            self.compute_curve(self.plot_model.references_data[k], ref_curve)
        # profiles
        if self.profile != -1:
            self.compute_curve(self.plot_model.profiles_data[self.profile][self.profile_point, :],
                               self.profile_curve)

    def compute_curve(self, data: np.ndarray, curve: pg.PlotDataItem,
                      use_reference: bool = True) -> None:
        x = self.plot_model.loader.timestamps
        if self.reference == -1 or not use_reference:
            y = data
        else:
            y = data - self.plot_model.references_data[self.reference]
        curve.setData(x, y)


# TemporalPlotWindow class #########################################################################

class TemporalPlotWindow(AbstractPlotWindow):

    reference_changed = Signal(int)
    profile_changed = Signal(int)

    def __init__(self, plot_model: PlotModel):
        super().__init__(plot_model, TemporalPlotWidget(plot_model))
        plot_model.closed.connect(self.on_close)
        self.setWindowTitle("Temporal profile")
        # checkbox to fix axes when hovering on Map:
        self.toolbar.addSeparator()
        self.checkbox_axes: QCheckBox = QCheckBox('Lock axes', self)
        self.checkbox_axes.setToolTip("When checked, keep axes ranges while hovering on Map."
                                      " Note that you can still zoom in/out on the plot.")
        self.checkbox_axes.stateChanged.connect(self.ctrl_axes)
        self.toolbar.addWidget(self.checkbox_axes)
        # reference icon
        self.toolbar.addSeparator()
        reference_icon: QLabel = QLabel()
        reference_icon.setPixmap(QIcon('icons:ref.png').pixmap(self.toolbar.iconSize()))
        self.toolbar.addWidget(reference_icon)
        # combobox to choose reference
        self.reference_combobox: QComboBox = QComboBox(self)
        proxy_reference_model = ProxyNoItemModel(self.plot_model.references, "No reference")
        self.reference_combobox.setModel(proxy_reference_model)
        proxy_reference_model.rowsAboutToBeRemoved.connect(
            self.update_reference_combobox_index_before_remove)
        self.reference_combobox.currentIndexChanged.connect(self.reference_combobox_index_changed)
        self.reference_changed.connect(self.plot_widget.change_reference)
        self.toolbar.addWidget(self.reference_combobox)
        # spacer
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(self.spacer)
        # export button
        self.toolbar.addWidget(self.export_button)
        # points show all action
        self.points_showall_action: QAction = QAction(QIcon('icons:eye_open.svg'), "Show all", self)
        self.points_showall_action.setToolTip("Show all point curves")
        self.points_showall_action.triggered.connect(self.plot_model.points.show_all_curves)
        # points hide all action
        self.points_hideall_action: QAction = QAction(QIcon('icons:eye_closed.svg'), "Hide all",
                                                      self)
        self.points_hideall_action.setToolTip("Hide all point curves")
        self.points_hideall_action.triggered.connect(self.plot_model.points.hide_all_curves)
        # points toolbar
        points_toolbar: QToolBar = QToolBar(self)
        points_icon: QLabel = QLabel()
        points_icon.setPixmap(QIcon('icons:points.png').pixmap(points_toolbar.iconSize()))
        points_toolbar.addWidget(points_icon)
        points_toolbar.addWidget(QLabel(" Points :"))
        points_toolbar.addAction(self.points_showall_action)
        points_toolbar.addAction(self.points_hideall_action)
        # points view
        self.points_view: QListView = QListView(parent=self)
        self.points_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.points_view.setModel(self.plot_model.points)
        # points widget
        points_widget: QWidget = QWidget()
        points_layout: QVBoxLayout = QVBoxLayout()
        points_layout.addWidget(points_toolbar)
        points_layout.addWidget(self.points_view)
        points_widget.setLayout(points_layout)
        # combobox to choose profile
        self.profile_combobox: QComboBox = QComboBox(self)
        self.profile_combobox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                                            self.profile_combobox.sizePolicy().verticalPolicy())
        proxy_profile_model = ProxyNoItemModel(self.plot_model.profiles, "No profile")
        self.profile_combobox.setModel(proxy_profile_model)
        proxy_profile_model.rowsAboutToBeRemoved.connect(
            self.update_profile_combobox_index_before_remove)
        self.profile_combobox.currentIndexChanged.connect(self.profile_combobox_index_changed)
        self.profile_changed.connect(self.plot_widget.change_profile)
        # profiles toolbar
        profiles_toolbar: QToolBar = QToolBar(self)
        profiles_icon: QLabel = QLabel()
        profiles_icon.setPixmap(QIcon('icons:profile.png').pixmap(profiles_toolbar.iconSize()))
        profiles_toolbar.addWidget(profiles_icon)
        profiles_toolbar.addWidget(self.profile_combobox)
        # spinbox to choose profile point
        self.profile_spinbox = QSpinBox(self)
        self.profile_spinbox.setKeyboardTracking(False)
        self.profile_spinbox.setDisabled(True)
        # slider to choose profile point
        self.profile_slider: QSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.profile_slider.setStyle(SliderLeftClickStyle())
        self.profile_slider.setDisabled(True)
        self.profile_spinbox.valueChanged.connect(self.profile_slider.setValue)
        self.profile_slider.valueChanged.connect(self.profile_spinbox.setValue)
        self.profile_slider.valueChanged.connect(self.plot_widget.change_profile_point)
        # profile label
        self.profile_label: QLabel = QLabel("position along profile in pixels")
        self.profile_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.profile_label.setDisabled(True)
        # profiles widget
        profiles_widget: QWidget = QWidget()
        profiles_layout: QVBoxLayout = QVBoxLayout()
        profiles_layout.addWidget(profiles_toolbar)
        profiles_slider_layout: QHBoxLayout = QHBoxLayout()
        profiles_slider_layout.addWidget(self.profile_spinbox)
        profiles_slider_layout.addWidget(self.profile_slider)
        profiles_layout.addLayout(profiles_slider_layout)
        profiles_layout.addWidget(self.profile_label)
        profiles_widget.setLayout(profiles_layout)
        profiles_widget.setMaximumHeight(profiles_widget.sizeHint().height())
        # references show all action
        self.references_showall_action: QAction = QAction(QIcon('icons:eye_open.svg'), "Show all",
                                                          self)
        self.references_showall_action.setToolTip("Show all reference curves")
        self.references_showall_action.triggered.connect(self.plot_model.references.show_all_curves)
        # references hide all action
        self.references_hideall_action: QAction = QAction(QIcon('icons:eye_closed.svg'), "Hide all",
                                                          self)
        self.references_hideall_action.setToolTip("Hide all reference curves")
        self.references_hideall_action.triggered.connect(self.plot_model.references.hide_all_curves)
        # references toolbar
        references_toolbar: QToolBar = QToolBar(self)
        references_icon: QLabel = QLabel()
        references_icon.setPixmap(QIcon('icons:ref.png').pixmap(points_toolbar.iconSize()))
        references_toolbar.addWidget(references_icon)
        references_toolbar.addWidget(QLabel(" References :"))
        references_toolbar.addAction(self.references_showall_action)
        references_toolbar.addAction(self.references_hideall_action)
        # references view
        self.references_view: QListView = QListView(parent=self)
        self.references_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.references_view.setModel(self.plot_model.references)
        # references widget
        references_widget: QWidget = QWidget()
        references_layout: QVBoxLayout = QVBoxLayout()
        references_layout.addWidget(references_toolbar)
        references_layout.addWidget(self.references_view)
        references_widget.setLayout(references_layout)
        # layout
        h_splitter: QSplitter = QSplitter(Qt.Orientation.Horizontal)
        h_splitter.setChildrenCollapsible(False)
        h_splitter.addWidget(self.plot_widget)
        v_splitter: QSplitter = QSplitter(Qt.Orientation.Vertical)
        v_splitter.setChildrenCollapsible(False)
        h_splitter.addWidget(v_splitter)
        v_splitter.addWidget(points_widget)
        v_splitter.addWidget(profiles_widget)
        v_splitter.addWidget(references_widget)
        self.layout().addWidget(h_splitter)

    @Slot(int)
    def ctrl_axes(self, state: int) -> None:
        if state == Qt.CheckState.Checked.value:
            self.plot_widget.plotItem.autoBtn.mode = 'fix'
        else:
            self.plot_widget.plotItem.autoBtn.mode = 'auto'
        self.plot_widget.plotItem.autoBtnClicked()

    @Slot()
    def on_close(self) -> None:
        self.profile_combobox.setCurrentIndex(-1)
        self.profile_slider.setValue(0)
        self.reference_combobox.setCurrentIndex(-1)
        self.checkbox_axes.setChecked(False)

    @Slot(int)
    def reference_combobox_index_changed(self, i: int) -> None:
        if i == -1:
            # combobox is empty so we reset it with the "no reference" item
            self.reference_combobox.setCurrentIndex(0)
        else:
            # for TemporalPlotWidget.reference, -1 means no reference, 0 means first reference...
            self.reference_changed.emit(i-1)

    @Slot(int)
    def profile_combobox_index_changed(self, i: int) -> None:
        if i == -1:
            # combobox is empty so we reset it with the "no reference" item
            self.profile_combobox.setCurrentIndex(0)
        else:
            if i == 0:
                self.profile_slider.setTickPosition(QSlider.TickPosition.NoTicks)
                self.profile_slider.setMinimum(0)
                self.profile_slider.setMaximum(0)
                self.profile_slider.setDisabled(True)
                self.profile_spinbox.setDisabled(True)
                self.profile_label.setDisabled(True)
            else:
                length: int = len(self.plot_model.profiles_data[i-1])
                if length <= 40:
                    self.profile_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
                else:
                    self.profile_slider.setTickPosition(QSlider.TickPosition.NoTicks)
                self.profile_slider.setTickInterval(1)
                self.profile_slider.setMinimum(0)
                self.profile_spinbox.setMinimum(0)
                self.profile_slider.setMaximum(length-1)
                self.profile_spinbox.setMaximum(length-1)
                self.profile_slider.setEnabled(True)
                self.profile_spinbox.setEnabled(True)
                self.profile_label.setEnabled(True)
            # for TemporalPlotWidget.profile, -1 means no profile, 0 means first profile...
            self.profile_changed.emit(i-1)
            self.profile_slider.setValue(0)
            self.profile_slider.valueChanged.emit(0)

    @Slot(QModelIndex, int, int)
    def update_reference_combobox_index_before_remove(self, parent: QModelIndex, first: int,
                                                      last: int) -> None:
        # pylint: disable=unused-argument
        previous_index = self.reference_combobox.currentIndex()
        if previous_index >= first and previous_index <= last:
            # otherwise QComboBox set currentIndex to first-1
            self.reference_combobox.setCurrentIndex(0)

    @Slot(QModelIndex, int, int)
    def update_profile_combobox_index_before_remove(self, parent: QModelIndex, first, last) -> None:
        # pylint: disable=unused-argument
        previous_index = self.profile_combobox.currentIndex()
        if previous_index >= first and previous_index <= last:
            # otherwise QComboBox set currentIndex to first-1
            self.profile_combobox.setCurrentIndex(0)


# TimeAxisItem class ###############################################################################

class TimeAxisItem(pg.DateAxisItem):
    """
    Based on pyqtgraph's DateAxisItem.
    Axis item that displays dates from unix timestamps, SI prefix
    for units is disabled and values are handled to be displayed in
    yyyy-mm-dd format.
    """

    def __init__(self, text: str, units: str):
        """
        Creates a new TimeAxisItem.

        Parameters
        ----------
        text : str
            text (without units) to display on the label for this axis
        units : str
            units for this axis
        """
        super().__init__()
        # to avoid unit scaling (unfit for dates) :
        self.enableAutoSIPrefix(False)
        self.setLabel(text=text, units=units)


# DateMarker class #################################################################################

class DateMarker(pg.InfiniteLine):
    """
    Based on pyqtgraph's InfiniteLine
    Vertical infinite line on plot, x-axis-position is synchronized with
    MainWindow's slider position
    overload some methods
    """

    pos_changed = Signal(int)

    base_pen = pg.functions.mkPen(0.5, width=3)
    dragged_pen = TimelineHandle.dragged_pen
    hover_pen = TimelineHandle.hover_pen

    def __init__(self, loader: Loader):
        self.loader: Loader = loader
        super().__init__(pen=DateMarker.base_pen, hoverPen=DateMarker.hover_pen, angle=90,
                         movable=True)
        self.setZValue(-100)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.sigDragged.connect(lambda _: self.setPen(DateMarker.dragged_pen))
        self.sigPositionChangeFinished.connect(lambda _: self.setPen(DateMarker.base_pen))

    def setPos(self, pos: Union[float, QPointF]) -> None:
        """ 
        Overload function
        Position can only be set to one of the values of the dataset
        (on x-axis, ie a band# or date)

        Parameters
        ----------
        pos : int, float, QPoint
            position (approx.) where the line should be set
        """
        if isinstance(pos, QPointF):
            pos = pos.x()
        if self.loader.timestamps is not None and pos not in self.loader.timestamps:
            pos, _ = get_nearest(self.loader.timestamps, pos)
        super().setPos(pos)

    def mouseDragEvent(self, ev):
        """
        Overload function
        emit signal that position changed, to update the position of the slider
        in MainWindow accordingly

        Parameters
        ----------
        ev : QMouseEvent
        """
        super().mouseDragEvent(ev)
        if ev.isAccepted():
            _, idx = get_nearest(self.loader.timestamps, self.getPos()[0])
            self.pos_changed.emit(self.loader.dataset.indexes[idx])
            if ev.isStart():
                QGuiApplication.instance().setOverrideCursor(Qt.CursorShape.DragMoveCursor)
            elif ev.isFinish():
                QGuiApplication.instance().restoreOverrideCursor()

    @Slot(int)
    def on_slider_changed(self, slidervalue: int) -> None:
        """
        Receive signal when MainWindow's slider position changed, update
        line position accordingly

        Parameters
        ----------
        slidervalue : int
            New position of slider tick.
        """
        assert self.loader.dataset is not None and self.loader.timestamps is not None
        self.setPos(self.loader.timestamps[self.loader.dataset.indexes.index(slidervalue)])
