# -*- coding: utf-8 -*-

from typing import Optional, Union

import warnings

import datetime

import numpy as np

import pyqtgraph as pg

from PySide6.QtCore import Qt, Slot, Signal, QModelIndex, QPointF

from PySide6.QtWidgets import QComboBox, QLabel, QCheckBox, QBoxLayout, QWidget, QSizePolicy

from PySide6.QtGui import QIcon, QColor, QGuiApplication

from insarviz.plot.PlotModel import PlotModel

from insarviz.plot.AbstractPlotView import AbstractPlotWindow, AbstractPlotWidget, ProxyNoItemModel

from insarviz.BandSlider import BandSlider

from insarviz.Roles import Roles

from insarviz.utils import get_nearest


# SpatialPlotWidget class ##########################################################################

class SpatialPlotWidget(AbstractPlotWidget):
    """
    spatial evolution plot (for profile only)
    """

    def __init__(self, plot_model: PlotModel):
        super().__init__(plot_model)
        # used by insarviz.exporters.myCSVExporter
        self.plotItem.insarviz_widget = self
        self.plotItem.setLabel('bottom', "Distance along profile line", units='pixel')
        self.point_marker = PointMarker()
        self.point_marker.sigPositionChanged.connect(self.point_marker_pos_changed)
        self.profile_curve: pg.PlotDataItem = pg.PlotDataItem(symbol='o', symbolSize=5,
                                                              antialias=True)
        self.profile_curve.sigPointsHovered.connect(self.on_points_hover)
        self.profile_curve.scatter.setData(hoverable=True, tip=None, hoverBrush='r', hoverSize=8)
        self.profile_curve.setSymbolPen(None)
        self.lowstd_curve = pg.PlotCurveItem(connect='finite', pen=None)
        self.highstd_curve = pg.PlotCurveItem(connect='finite', pen=None)
        self.profile_std: pg.FillBetweenItem = pg.FillBetweenItem(self.lowstd_curve,
                                                                  self.highstd_curve)
        self.profile_std.setZValue(-1.)
        self.profile: int = -1
        self.date: Optional[int] = None  # band number addex (starting from 0 like in python)
        self.reference: int = -1
        self.show_std: bool = False
        # signals and slots
        plot_model.profiles_updated.connect(self.update_curves)

    @Slot(int, int, list)
    def update_curves(self, first: int, last: int, roles: list[int]) -> None:
        if first <= self.profile <= last:
            profile_index = self.plot_model.profiles.index(self.profile, 0)
            if Roles.ComputeDataRole in roles:
                self.compute_profile_curve()
                self.compute_profile_std()
            if Roles.CurveColorRole in roles:
                color = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DecorationRole)
                self.profile_curve.setPen(color, width=2)
                self.profile_curve.setSymbolBrush(color)
                self.profile_std.setBrush(self.create_fill_color(color))
            if Qt.ItemDataRole.EditRole in roles:
                name = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DisplayRole)
                assert self.date is not None and self.plot_model.loader.timestamps is not None
                # remove tooltip for this curve
                self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)
                date = self.plot_model.loader.dates[self.date]
                date_string = (date.strftime('%Y-%m-%d') if isinstance(date, datetime.datetime)
                               else f"band {date}")
                self.profile_curve.opts["name"] = (f"{name} at {date_string}")

    @Slot(int)
    def change_profile(self, i: int) -> None:
        if self.profile != i:
            self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)
            if self.profile != -1:
                profile_index = self.plot_model.profiles.index(self.profile, 0)
                self.plot_model.profiles.setData(profile_index, None, Roles.ProfileSpatialRole)
        self.profile = i
        if self.profile != -1:
            profile_index = self.plot_model.profiles.index(self.profile, 0)
            color = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DecorationRole)
            self.profile_curve.setPen(color, width=2)
            self.profile_curve.setSymbolBrush(color)
            name = self.plot_model.profiles.data(profile_index, Qt.ItemDataRole.DisplayRole)
            assert self.date is not None and self.plot_model.loader.timestamps is not None
            date = self.plot_model.loader.dates[self.date]
            date_string = (date.strftime('%Y-%m-%d') if isinstance(date, datetime.datetime)
                           else f"band {date}")
            self.profile_curve.opts["name"] = (f"{name} at {date_string}")
            self.compute_profile_curve()
            self.profile_std.setBrush(self.create_fill_color(color))
            self.compute_profile_std()
            self.compute_limits()
            self.plotItem.setMouseEnabled(x=True, y=True)
            self.plotItem.addItem(self.profile_curve)
            if self.show_std:
                self.plotItem.addItem(self.profile_std)
            self.point_marker.setPos(0)
            self.point_marker_pos_changed()
            self.point_marker.length = len(self.plot_model.profiles_data[self.profile])
            self.plotItem.addItem(self.point_marker)
        else:
            # remove tooltip for this curve
            self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)
            self.profile_curve.opts["name"] = "no profile"
            self.plotItem.setMouseEnabled(x=False, y=False)
            self.plotItem.removeItem(self.profile_curve)
            self.plotItem.removeItem(self.profile_std)
            self.plotItem.removeItem(self.point_marker)
            self.point_marker.setPos(-1)
            self.point_marker.length = None

    @Slot(int)
    def change_date(self, i: int) -> None:
        assert self.plot_model.loader.dataset is not None
        assert i in self.plot_model.loader.dataset.indexes
        self.date = self.plot_model.loader.dataset.indexes.index(i)
        if self.profile != -1:
            self.compute_profile_curve()

    @Slot(int)
    def change_reference(self, i: int) -> None:
        self.reference = i
        if self.profile != -1:
            self.compute_limits()
            self.compute_profile_curve()
            self.compute_profile_std()

    # connected to SpatialPlotWindow.checkbox_std.stateChanged
    @Slot(int)
    def change_show_std(self, show: int) -> None:
        if show == Qt.CheckState.Checked.value:
            self.show_std = True
            if self.profile != -1:
                self.plotItem.addItem(self.profile_std)
        elif show == Qt.CheckState.Unchecked.value:
            self.show_std = False
            self.plotItem.removeItem(self.profile_std)

    def compute_profile_curve(self) -> None:
        """
        Compute the curve for profile.
        """
        if self.reference == -1:
            reference = np.zeros(len(self.plot_model.loader.dates))
        else:
            reference = np.array(self.plot_model.references_data[self.reference])
        length = self.plot_model.profiles_data[self.profile].shape[0]
        x = np.arange(length)
        assert self.date is not None
        y = self.plot_model.profiles_data[self.profile][:, self.date] - reference[self.date]
        self.profile_curve.setData(x, y)
        # remove tooltip for this curve
        self.profile_curve.sigPointsHovered.emit(self.profile_curve, [], None)

    def compute_profile_std(self) -> None:
        """
        Compute the standard deviation zones (mean +/- std) for profile.
        Set those zones to self.profiles_std.
        """
        if self.reference == -1:
            reference = np.zeros(len(self.plot_model.loader.dates))
        else:
            reference = np.array(self.plot_model.references_data[self.reference])
        x = np.arange(len(self.plot_model.profiles_data[self.profile]))
        with warnings.catch_warnings():
            # ignore RuntimeWarning for slices that contain only nans
            warnings.filterwarnings("ignore", category=RuntimeWarning,
                                    message="Mean of empty slice")
            warnings.filterwarnings("ignore", category=RuntimeWarning,
                                    message="Degrees of freedom <= 0 for slice.")
            profile_tmean = np.nanmean(self.plot_model.profiles_data[self.profile]
                                       - reference, axis=1)
            profile_std = np.nanstd(self.plot_model.profiles_data[self.profile] - reference, axis=1)
        y = profile_tmean - profile_std
        # remove single values surrounded by nans as pg.FillBetweenItem is bugged for those
        y[np.where(np.append(np.isnan(y[1:]), True)
                   & np.append([True], np.isnan(y[:-1])))] = np.nan
        self.lowstd_curve.setData(x, y)
        y = profile_tmean + profile_std
        # remove single values surrounded by nans as pg.FillBetweenItem is bugged for those
        y[np.where(np.append(np.isnan(y[1:]), True)
                   & np.append([True], np.isnan(y[:-1])))] = np.nan
        self.highstd_curve.setData(x, y)

    def compute_limits(self):
        """
        Compute and set axis limits.
        """
        if self.profile != -1:
            length = len(self.plot_model.profiles_data[self.profile])
            x_min = 0. - self.max_padding * length
            x_max = length + self.max_padding * length
            if self.reference == -1:
                reference = np.zeros(len(self.plot_model.loader))
            else:
                reference = np.array(self.plot_model.references_data[self.reference])
            with warnings.catch_warnings():
                # ignore RuntimeWarning for slices that contain only nans
                warnings.filterwarnings("ignore", category=RuntimeWarning,
                                        message="All-NaN slice encountered")
                y_min = np.nanmin(self.plot_model.profiles_data[self.profile] - reference)
                y_max = np.nanmax(self.plot_model.profiles_data[self.profile] - reference)
            y_delta = y_max - y_min
            y_min, y_max = y_min - self.max_padding*y_delta, y_max + self.max_padding*y_delta
            self.plotItem.setLimits(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max)
            self.plotItem.setXRange(x_min, x_max, padding=self.default_padding)
            self.plotItem.setYRange(y_min, y_max, padding=self.default_padding)

    def create_fill_color(self, color: QColor) -> QColor:
        fill_color = QColor(color)
        fill_color.setAlpha(96)
        return fill_color

    @Slot(object)
    def point_marker_pos_changed(self, _=None):
        if self.profile != -1:
            profile_index = self.plot_model.profiles.index(self.profile, 0)
            self.plot_model.profiles.setData(profile_index, self.point_marker.getPos()[0],
                                             Roles.ProfileSpatialRole)


# SpatialPlotWindow class ##########################################################################

class SpatialPlotWindow(AbstractPlotWindow):

    reference_changed = Signal(int)
    profile_changed = Signal(int)

    def __init__(self, plot_model: PlotModel):
        super().__init__(plot_model, SpatialPlotWidget(plot_model))
        plot_model.loader.data_loaded.connect(self.on_data_loaded)
        plot_model.closed.connect(self.on_close)
        self.setWindowTitle("Spatial profile")
        # profile icon
        self.toolbar.addSeparator()
        profiles_icon = QLabel()
        profiles_icon.setPixmap(QIcon('icons:profile.png').pixmap(self.toolbar.iconSize()))
        self.toolbar.addWidget(profiles_icon)
        # combobox to choose profile
        self.profile_combobox = QComboBox(self)
        self.toolbar.addWidget(self.profile_combobox)
        proxy_profile_model = ProxyNoItemModel(self.plot_model.profiles, "No profile")
        self.profile_combobox.setModel(proxy_profile_model)
        proxy_profile_model.rowsAboutToBeRemoved.connect(
            self.update_profile_combobox_index_before_remove)
        self.profile_combobox.currentIndexChanged.connect(self.profile_combobox_index_changed)
        self.profile_changed.connect(self.plot_widget.change_profile)
        # reference icon
        self.toolbar.addSeparator()
        reference_icon = QLabel()
        reference_icon.setPixmap(QIcon('icons:ref.png').pixmap(self.toolbar.iconSize()))
        self.toolbar.addWidget(reference_icon)
        # combobox to choose reference
        self.reference_combobox = QComboBox(self)
        self.toolbar.addWidget(self.reference_combobox)
        proxy_reference_model = ProxyNoItemModel(self.plot_model.references, "No reference")
        self.reference_combobox.setModel(proxy_reference_model)
        proxy_reference_model.rowsAboutToBeRemoved.connect(
            self.update_reference_combobox_index_before_remove)
        self.reference_combobox.currentIndexChanged.connect(self.reference_combobox_index_changed)
        self.reference_changed.connect(self.plot_widget.change_reference)
        # checkbox to show standard deviation
        self.toolbar.addSeparator()
        self.checkbox_std: QCheckBox = QCheckBox('Show standard deviation', self)
        self.checkbox_std.setToolTip("When checked, standard deviation across time will be \
                                displayed as a filled zone.")
        self.checkbox_std.stateChanged.connect(self.plot_widget.change_show_std)
        self.toolbar.addWidget(self.checkbox_std)
        # spacer
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(self.spacer)
        # export button
        self.toolbar.addWidget(self.export_button)
        # date slider
        self.band_slider = BandSlider(self.plot_model.loader)
        self.band_slider.value_changed.connect(self.plot_widget.change_date)
        # layout
        layout = self.layout()
        assert isinstance(layout, QBoxLayout)
        layout.addWidget(self.band_slider)
        layout.addWidget(self.plot_widget, stretch=1)

    @Slot(int)
    def on_data_loaded(self, band_index: int) -> None:
        self.band_slider.on_data_loaded(band_index)
        assert self.plot_model.loader.dataset is not None
        assert band_index in self.plot_model.loader.dataset.indexes
        self.band_slider.set_value(band_index)

    @Slot()
    def on_close(self) -> None:
        self.profile_combobox.setCurrentIndex(-1)
        self.checkbox_std.setChecked(False)
        self.reference_combobox.setCurrentIndex(-1)
        self.band_slider.on_close()

    @Slot(int)
    def reference_combobox_index_changed(self, i: int) -> None:
        if i == -1:
            # combobox is empty so we reset it with the "no reference" item
            self.reference_combobox.setCurrentIndex(0)
        else:
            # for SpatialPlotWidget.reference, -1 means no reference, 0 means first reference...
            self.reference_changed.emit(i-1)

    @Slot(int)
    def profile_combobox_index_changed(self, i: int) -> None:
        if i == -1:
            # combobox is empty so we reset it with the "no reference" item
            self.profile_combobox.setCurrentIndex(0)
        else:
            if i == 0:
                self.band_slider.setDisabled(True)
            else:
                self.band_slider.setEnabled(True)
            # for SpatialPlotWidget.profile, -1 means no profile, 0 means first profile...
            self.profile_changed.emit(i-1)

    @Slot(QModelIndex, int, int)
    def update_reference_combobox_index_before_remove(self, _: QModelIndex, first: int,
                                                      last: int) -> None:
        previous_index = self.reference_combobox.currentIndex()
        if first <= previous_index <= last:
            # otherwise QComboBox set currentIndex to first-1
            self.reference_combobox.setCurrentIndex(0)

    @Slot(QModelIndex, int, int)
    def update_profile_combobox_index_before_remove(self, _: QModelIndex, first: int,
                                                    last: int) -> None:
        previous_index = self.profile_combobox.currentIndex()
        if first <= previous_index <= last:
            # otherwise QComboBox set currentIndex to first-1
            self.profile_combobox.setCurrentIndex(0)


# PointMarker class ################################################################################

class PointMarker(pg.InfiniteLine):
    """
    Based on pyqtgraph's InfiniteLine
    Vertical infinite line on plot, x-axis-position is synchronized with
    SpatialPlotView point slider position
    """

    pos_changed = Signal(int)

    base_pen = pg.functions.mkPen(0.5, width=3)
    dragged_pen = pg.functions.mkPen("cyan", width=3)
    hover_pen = pg.functions.mkPen("red", width=3)

    def __init__(self):
        self.length: Optional[int] = None
        super().__init__(pen=PointMarker.base_pen, hoverPen=PointMarker.hover_pen, angle=90,
                         movable=True)
        self.setZValue(-100)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.sigDragged.connect(lambda _: self.setPen(PointMarker.dragged_pen))
        self.sigPositionChangeFinished.connect(lambda _: self.setPen(PointMarker.base_pen))

    def setPos(self, pos: Union[float, QPointF]) -> None:
        """
        Overloaded function
        Position can only be set to one of the values of the dataset
        (on x-axis, ie a band# or date)

        Parameters
        ----------
        pos : int, float, QPoint
            position (approx.) where the line should be set
        """
        if isinstance(pos, QPointF):
            pos = pos.x()
        if self.length is not None:
            pos, _ = get_nearest(range(self.length), pos)
        super().setPos(pos)

    def mouseDragEvent(self, ev) -> None:
        super().mouseDragEvent(ev)
        if ev.isAccepted():
            if ev.isStart():
                QGuiApplication.instance().setOverrideCursor(Qt.CursorShape.DragMoveCursor)
            elif ev.isFinish():
                QGuiApplication.instance().restoreOverrideCursor()
