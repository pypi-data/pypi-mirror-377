#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" MapView

This module handles the creation of the Map view (image display of a band data)
 and user interactions with it (pan, zoom, data selection...).
 Works with the module MapModel (as in a Model/View architecture).

Contains class:
    * MapView
"""


# imports ###################################################################

from typing import Optional
import rasterio

from OpenGL import GL

from PySide6.QtCore import QSize, Slot, Signal, Qt, QPoint, QPointF, QEvent

from PySide6.QtWidgets import QToolTip, QWidget, QMenu, QMessageBox

from PySide6.QtGui import (
    QPainter, QMouseEvent, QIcon, QCursor, QColor, QAction, QActionGroup, QGuiApplication
)

from insarviz.map.AbstractMapView import AbstractMapView

from insarviz.map.MapModel import MapModel

from insarviz.linalg import matrix

from insarviz.map.layers.SelectionLayer import (
    SelectionItem, SelectionPoint, SelectionProfile, SelectionReference
)
from insarviz.map.layers.Layer import Layer

# MapView #######################################################################

class MapView(AbstractMapView):

    size_threshold_confirmation_selection_item = 1000000

    POINTS: int = 1
    PROFILE: int = 2
    REF: int = 3

    # send the position of the mouse in data coordinate (int, int) and the band number to PlotModel
    pointer_changed = Signal(tuple, int)
    viewport_matrix_changed = Signal(object)
    interaction_changed = Signal(int)
    request_lock_axes = Signal()

    def __init__(self, map_model: MapModel, parent: QWidget):
        """
        Generate Map, a QOpenGLWidget display of the displacement data. Zoom
        level can be interactively set through mouse wheel or right-click+drag.
        View position on the Map can be interactively set through left-click+
        drag. View is synchronized to Minimap.

        Parameters
        ----------
        map_model : MapModel
            Model managing the data for Map and Minimap.
        """
        super().__init__(map_model, parent)
        # selection item that the user is creating before adding it to the selection layer
        self.selection_item: Optional[SelectionItem] = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.menu = QMenu()
        self.action_group = QActionGroup(self)
        self.lock_plot_axes_action = QAction("Lock axes", self)
        self.lock_plot_axes_action.triggered.connect(self.lock_plot_axes)
        self.menu.addAction(self.lock_plot_axes_action)
        self.action_group.addAction(self.lock_plot_axes_action)

        self.create_temp_point_action = QAction("Create temporary point", self)
        self.create_temp_point_action.setIcon(QIcon('icons:points.png'))
        self.create_temp_point_action.triggered.connect(self.create_temp_point)
        self.menu.addAction(self.create_temp_point_action)
        self.action_group.addAction(self.create_temp_point_action)

        self.create_point_action = QAction("Create point", self)
        self.create_point_action.setIcon(QIcon('icons:points.png'))
        self.create_point_action.triggered.connect(self.create_point)
        self.menu.addAction(self.create_point_action)
        self.action_group.addAction(self.create_point_action)
        self.create_profile_action = QAction("Create profile", self)
        self.create_profile_action.setIcon(QIcon('icons:profile.png'))
        self.create_profile_action.triggered.connect(self.create_profile)
        self.menu.addAction(self.create_profile_action)
        self.action_group.addAction(self.create_profile_action)
        self.create_reference_action = QAction("Create reference", self)
        self.create_reference_action.setIcon(QIcon('icons:ref.png'))
        self.create_reference_action.triggered.connect(self.create_reference)
        self.menu.addAction(self.create_reference_action)
        self.action_group.addAction(self.create_reference_action)
        self.copy_coordinates_action = QAction("Copy coordinates to clipboard", self)
        self.copy_coordinates_action.triggered.connect(self.copy_coordinates_to_clipboard)
        self.menu.addAction(self.copy_coordinates_action)
        self.action_group.addAction(self.copy_coordinates_action)

    # opengl

    def sizeHint(self) -> QSize:
        return QSize(300, 300)

    def paintGL(self) -> None:
        glfunc = self.context().functions()
        painter = QPainter(self)
        # FIX for issue #150
        # Qpainter seems to need to "paint" something in order for it to correctly give back the
        # global OpenGL state (I can't find why)
        painter.fillRect(0, 0, 0, 0, QColor("transparent"))
        # END FIX
        painter.beginNativePainting()
        glfunc.glClear(GL.GL_COLOR_BUFFER_BIT)
        painter.endNativePainting()
        # layers is reversed so first layer is displayed last (i.e. upon the others)

        show_params = Layer.ShowParams()
        for layer in reversed(self.map_model.layer_model.layers):
            if layer.visible:
                layer.show(self.view_matrix, self.projection_matrix, show_params,
                           painter=painter, vao=self.vao, glfunc=glfunc)
                layer.update_show_params(show_params)
        if self.selection_item is not None:
            self.selection_item.show(self.view_matrix, painter, preview=True)
        painter.end()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if (self.map_model.current_band_index is not None and (not self.left_drag) and (not self.right_drag)
                and self.selection_item is None):
            self.pointer_changed.emit((), None)
            if e.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
                self.p0 = (*self.get_texture_coordinate(int(e.position().x()), int(e.position().y())),
                           int(e.position().x()), int(e.position().y()))
            if e.button() == Qt.MouseButton.LeftButton:
                if self.interaction == self.INTERACTIVE:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                else:
                    # check if pointer inside dataset
                    if ((0 <= self.p0[0] < self.map_model.tex_width)
                            and (0 <= self.p0[1] < self.map_model.tex_height)):
                        if self.interaction == self.POINTS:
                            self.create_point()
                        elif self.interaction == self.PROFILE:
                            self.create_profile()
                        elif self.interaction == self.REF:
                            self.create_reference()
            elif e.button() == Qt.MouseButton.RightButton:
                self.show_context_menu()
        super().mousePressEvent(e)
        # prevent right drag because right press launch context menu thus right release is missed
        self.right_drag = False

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        # check if data loaded (needed when opening without data)
        if self.map_model.current_band_index is not None:
            if (not self.left_drag) and (not self.right_drag):
                self.p0 = (*self.get_texture_coordinate(int(e.position().x()), int(e.position().y())),
                           int(e.position().x()), int(e.position().y()))
                i, j = int(self.p0[0]), int(self.p0[1])
                # check if pointer inside map
                if (0 <= i < self.map_model.tex_width) and (0 <= j < self.map_model.tex_height):
                    self.pointer_changed.emit((i, j), self.map_model.current_band_index)
                else:
                    self.pointer_changed.emit((), None)
            if self.interaction == self.INTERACTIVE:
                if self.left_drag:
                    # get the data coordinates of the point we are dragging
                    x0, y0, _, _ = self.p0
                    # get the data coordinates of where the cursor no is
                    x1, y1 = self.get_texture_coordinate(int(e.position().x()),
                                                         int(e.position().y()))
                    # make the difference between both and move the center of the view accordingly
                    dx, dy = x1-x0, y1-y0
                    self.pan(-dx, -dy)
            elif self.interaction == self.POINTS and self.left_drag:
                if self.selection_item is not None:
                    assert isinstance(self.selection_item, SelectionPoint)
                    x, y = self.get_texture_coordinate(int(e.position().x()),
                                                       int(e.position().y()))
                    dx = abs(int(x) - self.selection_item.x) + 1
                    dy = abs(int(y) - self.selection_item.y) + 1
                    r = min(max(dx, dy), self.selection_item.x+1, self.selection_item.y+1,
                            self.map_model.tex_width - self.selection_item.x,
                            self.map_model.tex_height - self.selection_item.y)
                    if self.selection_item.r != r:
                        self.selection_item.set_r(r)
                        self.paint()
            elif self.interaction == self.PROFILE:
                if self.selection_item is not None:
                    assert isinstance(self.selection_item, SelectionProfile)
                    x, y = self.get_texture_coordinate(int(e.position().x()),
                                                       int(e.position().y()))
                    x, y = int(x), int(y)
                    if (0 <= x < self.map_model.tex_width and 0 <= y < self.map_model.tex_height):
                        if (x != self.selection_item.points[-1][0] or
                                y != self.selection_item.points[-1][1]):
                            if len(self.selection_item.points) > 1:
                                self.selection_item.remove_last_point()
                            self.selection_item.add_point(x, y)
                            self.paint()
            elif self.interaction == self.REF and self.left_drag:
                if self.selection_item is not None:
                    assert isinstance(self.selection_item, SelectionReference)
                    x, y = self.get_texture_coordinate(int(e.position().x()),
                                                       int(e.position().y()))
                    x, y = int(x), int(y)
                    x = max(x, 0)
                    x = min(x, self.map_model.tex_width - 1)
                    y = max(y, 0)
                    y = min(y, self.map_model.tex_height - 1)
                    x0, y0 = int(self.p0[0]), int(self.p0[1])
                    left, right = min(x, x0), max(x, x0)
                    top, bottom = min(y, y0), max(y, y0)
                    if self.selection_item.get_rect() != (left, top, right, bottom):
                        self.selection_item.set_rect(left, top, right, bottom)
                        self.paint()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if self.interaction == self.INTERACTIVE and e.button() == Qt.MouseButton.LeftButton and self.left_drag:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif self.interaction == self.POINTS and e.button() == Qt.MouseButton.LeftButton:
            if self.selection_item is not None:
                assert isinstance(self.selection_item, SelectionPoint)
                size = (2*self.selection_item.r-1)**2
                if size > self.size_threshold_confirmation_selection_item:
                    if QMessageBox.question(self, "Insarviz",
                                            f"You are about to add a point of size {size}, it can "
                                            "take some time to compute its mean.\nAre you sure ?",
                                            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok,
                                            QMessageBox.StandardButton.Ok) == QMessageBox.StandardButton.Cancel:
                        self.selection_item = None
                        self.paint()
                        super().mouseReleaseEvent(e)
                        return None
                self.map_model.layer_model.add_selection_point(self.selection_item)
                self.selection_item = None
            self.set_interaction(self.INTERACTIVE)
        elif self.interaction == self.PROFILE and e.button() == Qt.MouseButton.LeftButton:
            if self.selection_item is not None:
                assert isinstance(self.selection_item, SelectionProfile)
                if len(self.selection_item.points) > 1:
                    self.selection_item.remove_last_point()
                    x, y = self.get_texture_coordinate(int(e.position().x()),
                                                       int(e.position().y()))
                    x, y = int(x), int(y)
                    if (0 <= x < self.map_model.tex_width and 0 <= y < self.map_model.tex_height):
                        self.selection_item.add_point(x, y)
                        self.selection_item.add_point(x, y)
                        self.paint()
        elif self.interaction == self.PROFILE and e.button() == Qt.MouseButton.RightButton:
            if self.selection_item is not None:
                assert isinstance(self.selection_item, SelectionProfile)
                self.selection_item.remove_last_point()
                if len(self.selection_item.points) > 1:
                    self.map_model.layer_model.add_selection_profile(self.selection_item)
                self.selection_item = None
                self.paint()
            self.set_interaction(self.INTERACTIVE)
        elif self.interaction == self.REF and e.button() == Qt.MouseButton.LeftButton:
            if self.selection_item is not None:
                assert isinstance(self.selection_item, SelectionReference)
                ref = self.selection_item
                size = (ref.right - ref.left + 1) * (ref.bottom - ref.top + 1)
                if size > self.size_threshold_confirmation_selection_item:
                    if QMessageBox.question(self, "Insarviz",
                                            f"You are about to add a reference of size {size}, it "
                                            "can take some time to compute its mean.\n"
                                            "Are you sure ?",
                                            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok,
                                            QMessageBox.StandardButton.Ok) == QMessageBox.StandardButton.Cancel:
                        self.selection_item = None
                        self.paint()
                        super().mouseReleaseEvent(e)
                        return None
                self.map_model.layer_model.add_selection_reference(self.selection_item)
                self.selection_item = None
            self.set_interaction(self.INTERACTIVE)
        super().mouseReleaseEvent(e)

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self.pointer_changed.emit((), None)

    def update_view_matrix(self) -> None:
        super().update_view_matrix()
        viewport_matrix = matrix.mul(self.view_matrix_inverse,
                                     matrix.scale(self.width(), self.height()))
        self.viewport_matrix_changed.emit(viewport_matrix)

    def show_context_menu(self):
        if ((0 <= self.p0[0] < self.map_model.tex_width)
                and (0 <= self.p0[1] < self.map_model.tex_height)):
            self.action_group.setEnabled(True)
        else:
            self.action_group.setDisabled(True)
        action = self.menu.exec(self.mapToGlobal(QPoint(self.p0[2], self.p0[3])))
        if action in (self.create_point_action, self.create_reference_action):
            # start left dragging to edit the newly created selection item
            # not required for profile because its edition does not use dragging
            self.left_drag = True
        # raise a mouseMoveEvent to update the position of the mouse after clicking on the menu
        event = QMouseEvent(QEvent.MouseMove, QPointF(self.mapFromGlobal(QCursor.pos())),
                            Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.mouseMoveEvent(event)

    @Slot()
    def copy_coordinates_to_clipboard(self):
        _,_,x_widget,y_widget = self.p0
        dataset = self.map_model.loader.dataset
        if dataset.crs is not None:
            x,y = dataset.xy(y_widget,x_widget)
            lon, lat = rasterio.warp.transform(dataset.crs,
                                               rasterio.crs.CRS.from_epsg(4326),
                                               [x], [y])
            QGuiApplication.clipboard().setText(f"{lat[0]},{lon[0]}")

    @Slot()
    def lock_plot_axes(self):
        i, j = int(self.p0[0]), int(self.p0[1])
        assert (0 <= i < self.map_model.tex_width) and (0 <= j < self.map_model.tex_height)
        self.pointer_changed.emit((i, j), self.map_model.current_band_index)
        self.request_lock_axes.emit()

    @Slot()
    def create_point(self):
        i, j = int(self.p0[0]), int(self.p0[1])
        assert (0 <= i < self.map_model.tex_width) and (0 <= j < self.map_model.tex_height)
        self.set_interaction(self.POINTS)
        self.selection_item = SelectionPoint(i, j, 1)
        self.paint()

    @Slot()
    def create_temp_point(self):
        i, j = int(self.p0[0]), int(self.p0[1])
        assert (0 <= i < self.map_model.tex_width) and (0 <= j < self.map_model.tex_height)
        selection_item = SelectionPoint(i, j, 1)
        selection_item.color = QColor('red')
        selection_item.name = "Temporary Point"
        self.map_model.layer_model.add_selection_point(selection_item)

    @Slot()
    def create_reference(self):
        i, j = int(self.p0[0]), int(self.p0[1])
        assert (0 <= i < self.map_model.tex_width) and (0 <= j < self.map_model.tex_height)
        self.set_interaction(self.REF)
        self.selection_item = SelectionReference(i, j)
        self.paint()

    @Slot()
    def create_profile(self):
        i, j = int(self.p0[0]), int(self.p0[1])
        assert (0 <= i < self.map_model.tex_width) and (0 <= j < self.map_model.tex_height)
        self.set_interaction(self.PROFILE)
        self.selection_item = SelectionProfile(i, j, 1)
        self.paint()

    @Slot(tuple)
    def update_mouse_tooltip(self, info: tuple) -> None:
        if info == ():
            QToolTip.hideText()
        else:
            x, y, _, value = info
            x_data, y_data, x_widget, y_widget = self.p0
            x_data, y_data = int(x_data), int(y_data)
            if (not x == x_data) or (not y == y_data):
                print("pointer info is too late")
                return None
            p = self.mapToGlobal(QPoint(x_widget, y_widget))
            # force the tooltip to update its position even if text remain the same
            # QToolTip.showText(p, "")
            QToolTip.showText(p, f"x:{x}\ny:{y}\nval:{value:.3f}")

    # interaction
    @Slot(int)
    def set_interaction(self, value: int) -> None:
        if value != self.interaction:
            self.selection_item = None
            if value == self.INTERACTIVE:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
            self.paint()
            super().set_interaction(value)
            self.interaction_changed.emit(value)
