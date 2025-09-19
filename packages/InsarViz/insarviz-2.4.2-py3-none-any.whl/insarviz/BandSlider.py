#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Union

import datetime

import numpy as np

from PySide6.QtCore import Qt, QPointF, Slot, Signal, QSignalBlocker, QEvent

from PySide6.QtGui import QGuiApplication, QKeyEvent

from PySide6.QtWidgets import (
    QWidget, QStyle, QProxyStyle, QStyleOption, QStyleHintReturn, QSlider, QLabel,
    QSpinBox, QHBoxLayout, QVBoxLayout, QGroupBox
)

import pyqtgraph as pg

from insarviz.utils import get_nearest

from insarviz.Loader import Loader


class SliderLeftClickStyle(QProxyStyle):
    """
    ProxyStyle overriding the mouse button used to move a slider on click (all buttons now move
    the slider to the position under the mouse)

    see https://stackoverflow.com/a/26281608
    """

    def styleHint(self, hint: QStyle.StyleHint, option: Optional[QStyleOption] = None,
                  widget: Optional[QWidget] = None,
                  returnData: Optional[QStyleHintReturn] = None) -> int:
        if hint == QStyle.StyleHint.SH_Slider_AbsoluteSetButtons:
            return (Qt.MouseButton.LeftButton | Qt.MouseButton.MiddleButton |
                    Qt.MouseButton.RightButton).value
        return super().styleHint(hint, option, widget, returnData)


class TimelineTick(pg.InfiniteLine):

    tick_pen = pg.functions.mkPen("grey", width=2)
    hover_pen = pg.functions.mkPen("r", width=3)

    def __init__(self, pos: float, tooltip: str = ""):
        super().__init__(pos=pos, pen=TimelineTick.tick_pen,
                         hoverPen=TimelineTick.hover_pen, angle=90, movable=True)
        self.setToolTip(tooltip)

    def mouseDragEvent(self, ev) -> None:
        pass

    def mouseClickEvent(self, ev) -> None:
        self.sigClicked.emit(self, ev)


class TimelineHandle(pg.InfiniteLine):

    handle_pen = pg.functions.mkPen("blue", width=3)
    dragged_pen = pg.functions.mkPen("cyan", width=3)
    hover_pen = pg.functions.mkPen("red", width=3)

    def __init__(self, loader: Loader):
        self.loader = loader
        super().__init__(pen=TimelineHandle.handle_pen, hoverPen=TimelineHandle.hover_pen,
                         angle=90, movable=True)
        self.addMarker('<|>')
        self.setZValue(1)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.sigDragged.connect(lambda x: x.setPen(TimelineHandle.dragged_pen))
        self.sigPositionChangeFinished.connect(lambda x: x.setPen(TimelineHandle.handle_pen))

    def setPos(self, pos: Union[float, QPointF]) -> None:
        if isinstance(pos, QPointF):
            pos = pos.x()
        elif isinstance(pos, (list, tuple, np.ndarray)):
            pos = pos[0]
        if self.loader.timestamps is not None and pos not in self.loader.timestamps:
            pos, _ = get_nearest(self.loader.timestamps, pos)
        super().setPos(pos)
        self.setToolTip(str(datetime.date.fromtimestamp(pos)))

    def mouseDragEvent(self, ev) -> None:
        super().mouseDragEvent(ev)
        if ev.isAccepted():
            if ev.isStart():
                QGuiApplication.instance().setOverrideCursor(Qt.CursorShape.DragMoveCursor)
            elif ev.isFinish():
                QGuiApplication.instance().restoreOverrideCursor()


class TimelineSlider(pg.PlotWidget):

    value_changed = Signal(int)

    def __init__(self, loader: Loader, parent: Optional[QWidget] = None):
        self.date_axis = pg.DateAxisItem()
        self.date_axis.enableAutoSIPrefix(False)
        super().__init__(parent=parent, axisItems={'bottom': self.date_axis}, enableMenu=False)
        self.loader = loader
        self.setMouseEnabled(y=False)
        plot_item = self.getPlotItem()
        plot_item.hideAxis('left')
        plot_item.hideButtons()
        self.ticks: list[TimelineTick] = []
        self.handle: Optional[TimelineHandle] = None
        self.setMaximumHeight(48)
        self.hide()

    def clear(self) -> None:
        if self.handle is not None:
            self.handle.sigPositionChanged.disconnect(self.on_handle_position_changed)
        for tick in self.ticks:
            tick.sigClicked.disconnect(self.on_tick_click)
        super().clear()

    @Slot(int)
    def on_data_loaded(self) -> None:
        assert self.loader.timestamps is not None
        # set the min max range of the x axis
        timedelta = self.loader.timestamps[-1] - self.loader.timestamps[0]
        xmin = self.loader.timestamps[0] - 0.1*timedelta
        xmax = self.loader.timestamps[-1] + 0.1*timedelta
        self.setLimits(xMin=xmin, xMax=xmax)
        self.getPlotItem().getViewBox().setXRange(self.loader.timestamps[0],
                                                  self.loader.timestamps[-1], padding=0.1)
        # date marker
        for d, t in zip(self.loader.dates, self.loader.timestamps):
            assert isinstance(d, datetime.datetime)
            tooltip = str(d.date())
            tick = TimelineTick(t, tooltip)
            tick.sigClicked.connect(self.on_tick_click)
            self.addItem(tick)
            self.ticks.append(tick)
        self.handle = TimelineHandle(self.loader)
        self.handle.sigPositionChanged.connect(self.on_handle_position_changed)
        self.addItem(self.handle)

    @Slot(int)
    def set_value(self, band_index: int) -> None:
        assert self.loader.dataset is not None and self.loader.timestamps is not None
        assert self.handle is not None
        self.handle.setPos(self.loader.timestamps[self.loader.dataset.indexes.index(band_index)])

    @Slot(object, object)
    def on_tick_click(self, tick: TimelineTick, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            assert self.handle is not None
            self.handle.setPos(tick.getXPos())

    @Slot(object)
    def on_handle_position_changed(self, _: TimelineHandle) -> None:
        assert self.loader.dataset is not None and self.loader.timestamps is not None
        assert self.handle is not None
        assert self.handle.getXPos() in self.loader.timestamps
        index = self.loader.dataset.indexes[
            np.where(self.loader.timestamps == self.handle.getXPos())[0][0]]
        self.value_changed.emit(index)


class BandSlider(QWidget):

    value_changed = Signal(int)
    reference_band_changed = Signal(object)

    def __init__(self, loader: Loader, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.loader = loader
        self.loader.reference_band_index_changed.connect(self.set_reference_band_index)
        self.reference_band_changed.connect(self.loader.set_reference_band)
        # label
        self.date_label = QLabel("")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.date_label.setMaximumHeight(20)
        # reference band spin box
        self.reference_band_groupbox = QGroupBox("Reference Band")
        self.reference_band_groupbox.setCheckable(True)
        self.reference_band_groupbox.setChecked(False)
        self.reference_band_groupbox.clicked.connect(self.on_reference_band_groupbox_clicked)
        self.reference_band_layout = QHBoxLayout()
        self.reference_band_groupbox.setLayout(self.reference_band_layout)
        self.reference_band_setter = mySpinBox()
        self.reference_band_setter.setRange(0, 0)
        self.reference_band_setter.editingFinished.connect(
            self.on_reference_band_setter_editingfinished)
        self.reference_band_layout.addWidget(self.reference_band_setter)
        # spin box
        self.band_setter = QSpinBox()
        self.band_setter.setRange(1, 1)
        self.band_setter.setKeyboardTracking(False)
        # slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setStyle(SliderLeftClickStyle())
        self.slider.setMinimum(1)
        self.slider.setMaximum(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        # allow arrow keys press to change date
        self.slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # timeline slider
        self.timeline_slider = TimelineSlider(self.loader)
        # signals and slots
        self.band_setter.valueChanged.connect(self.set_value)
        self.slider.valueChanged.connect(self.set_value)
        self.timeline_slider.value_changed.connect(self.set_value)
        # layout
        self.layoutH = QHBoxLayout()
        self.layoutH.addWidget(self.date_label)
        self.layoutH.addWidget(self.band_setter)
        self.layoutH.addWidget(self.slider)
        self.layoutH.addWidget(self.reference_band_groupbox)
        self.layoutV = QVBoxLayout()
        self.layoutV.addLayout(self.layoutH)
        self.layoutV.addWidget(self.timeline_slider)
        self.setLayout(self.layoutV)
        # set disabled
        self.setDisabled(True)

    @Slot()
    def on_close(self) -> None:
        self.setDisabled(True)
        self.slider.blockSignals(True)
        self.slider.setValue(1)
        self.slider.blockSignals(False)
        with QSignalBlocker(self.band_setter):
            self.band_setter.setValue(1)
        with QSignalBlocker(self.reference_band_setter):
            self.reference_band_setter.setValue(1)
        with QSignalBlocker(self.reference_band_groupbox):
            self.reference_band_groupbox.setChecked(False)
        self.timeline_slider.clear()
        self.timeline_slider.hide()
        self.date_label.setText("File->Open to load data")
        self.date_label.setEnabled(True)

    @Slot(int)
    def on_data_loaded(self, _: int):
        self.set_range(1, len(self.loader))
        if isinstance(self.loader.dates[0], datetime.datetime):
            self.timeline_slider.on_data_loaded()
            self.timeline_slider.show()
        else:
            self.timeline_slider.hide()

    def set_range(self, start: int, end: int) -> None:
        self.slider.setMinimum(start)
        self.slider.setMaximum(end)
        self.band_setter.setRange(start, end)
        self.reference_band_setter.setRange(start, end)

    @Slot(int)
    def set_value(self, v: int) -> None:
        self.slider.setValue(v)
        self.band_setter.setValue(v)
        if not self.timeline_slider.isHidden():
            self.timeline_slider.set_value(v)
        assert self.loader.dataset is not None
        date = self.loader.dates[self.loader.dataset.indexes.index(v)]
        if isinstance(date, datetime.datetime):
            self.date_label.setText(f"{date.date()} - Band #")
        else:
            self.date_label.setText('Band #')
        self.value_changed.emit(v)

    @Slot(bool)
    def on_reference_band_groupbox_clicked(self, checked: bool) -> None:
        if not checked:
            self.reference_band_changed.emit(None)
        else:
            self.reference_band_changed.emit(self.reference_band_setter.value())

    @Slot(object)
    def set_reference_band_index(self, index: Optional[int]) -> None:
        if index is None:
            self.reference_band_groupbox.setChecked(False)
        else:
            index = int(index)
            self.reference_band_groupbox.setChecked(True)
            self.reference_band_setter.setValue(index)

    @Slot()
    def on_reference_band_setter_editingfinished(self) -> None:
        self.reference_band_changed.emit(self.reference_band_setter.value())


class mySpinBox(QSpinBox):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        # accept "Enter" key press that would otherwise be forwarded to parent widget
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            e.accept()

    def changeEvent(self, e: QEvent) -> None:
        # hide line edit when disabled
        if e.type() == QEvent.Type.EnabledChange:
            if not self.isEnabled():
                self.lineEdit().setText("None")
        super().changeEvent(e)
