#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" MinimapView

This module handles the creation of the Minimap view (general image display
of a band data) and user interactions with it (pan and zoom).
Works with the module MapModel (as in a Model/View architecture).

Contains class:
* MinimapView
"""
# imports ###################################################################

from PySide6.QtCore import Qt, QSize, Signal, Slot

from PySide6.QtGui import (
    QMouseEvent, QWheelEvent, QMatrix4x4
)

from PySide6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader

from PySide6.QtWidgets import QWidget

from OpenGL import GL

from insarviz.map.AbstractMapView import AbstractMapView

from insarviz.map.MapModel import MapModel

from insarviz.map.layers.Layer import MainLayer

from insarviz.map.Shaders import VIEWPORTRECT_VERT_SHADER, VIEWPORTRECT_FRAG_SHADER

from insarviz.linalg import matrix

# MiniMapView ##################################################################


class MinimapView(AbstractMapView):
    """
    Minimap
    This is a general view of the data. A white rectangle
    shows the area cureently displayed in Map (zoom/pan synchronized).
    """

    CLICK = 1

    pan_map_view = Signal(float, float)
    zoom_map_view = Signal(float, float, float)
    set_center_map_view = Signal(float, float)

    def __init__(self, map_model: MapModel, parent: QWidget):
        super().__init__(map_model, parent)
        # model matrix of the rectangle figuring MapView's viewport (in data coordinate system)
        self.mapview_viewport_matrix = matrix.identity()
        self.program: QOpenGLShaderProgram
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def initializeGL(self) -> None:
        super().initializeGL()
        glfunc = self.context().functions()
        glfunc.glDisable(GL.GL_BLEND)
        # shaders for the rectangle figuring MapView's viewport
        self.program = QOpenGLShaderProgram()
        self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex,
                                             VIEWPORTRECT_VERT_SHADER)
        self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment,
                                             VIEWPORTRECT_FRAG_SHADER)
        self.program.link()
        self.program.bind()
        self.program.setUniformValue(self.program.uniformLocation('rect_color'), 1., 1., 1., 1.)
        self.program.release()

    def sizeHint(self) -> QSize:
        return QSize(100, 100)

    def paintGL(self) -> None:
        glfunc = self.context().functions()
        glfunc.glClear(GL.GL_COLOR_BUFFER_BIT)
        ####
        for layer in self.map_model.layer_model.layers:
            if isinstance(layer, MainLayer):
                layer.show(self.view_matrix, self.projection_matrix, MainLayer.ShowParams(), vao=self.vao, glfunc=glfunc,
                           blend=False)
        # white rectangle figuring MapView's viewport
        self.vao.bind()
        self.program.bind()
        self.program.setUniformValue(self.program.uniformLocation('model_matrix'),
                                     QMatrix4x4(matrix.flatten(self.mapview_viewport_matrix)))
        self.program.setUniformValue(self.program.uniformLocation('view_matrix'),
                                     QMatrix4x4(matrix.flatten(self.view_matrix)))
        self.program.setUniformValue(self.program.uniformLocation('projection_matrix'),
                                     QMatrix4x4(matrix.flatten(self.projection_matrix)))
        glfunc.glDrawArrays(GL.GL_LINE_LOOP, 0, 4)
        self.program.release()
        self.vao.release()

    # interaction

    def mousePressEvent(self, e: QMouseEvent) -> None:
        # check if data loaded
        if self.map_model.current_band_index is not None:
            if self.interaction == self.INTERACTIVE:
                # NOTE self.p0 does not match AbstractMapView.p0:
                # it is the last position of the mouse while pressed,
                # not the position of the last mouse press
                self.p0 = (*self.get_texture_coordinate(int(e.position().x()), int(e.position().y())),
                           int(e.position().x()), int(e.position().y()))
                self.p_prev = self.p0
                if e.button() == Qt.MouseButton.LeftButton:
                    self.interaction = self.CLICK
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if self.interaction == self.CLICK or self.left_drag or self.right_drag:
            x_data0, y_data0, x_widget0, y_widget0 = self.p0
            x_data1, y_data1, x_widget1, y_widget1 = (*self.get_texture_coordinate(int(e.position().x()), int(e.position().y())),
                                                      int(e.position().x()), int(e.position().y()))
            dx, dy = x_data1-x_data0, y_data1-y_data0
            if self.interaction == self.CLICK:
                # if the cursor has moved away from the press position buffer zone
                if abs(x_widget1 - x_widget0) + abs(y_widget1 - y_widget0) > 4:
                    self.interaction = self.INTERACTIVE
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
            elif self.left_drag:
                self.pan_map_view.emit(dx, dy)
                # NOTE self.p0 does not match AbstractMapView.p0:
                # it is the last position of the mouse while pressed,
                # not the position of the last mouse press
                self.p0 = x_data1, y_data1, x_widget1, y_widget1
            elif self.right_drag:
                # make the difference in view coordinates between the cursor previous
                # and current positions and zoom accordingly
                _, _, x_prev, y_prev = self.p_prev
                self.zoom_map_view.emit((x_widget1 - x_prev) -
                                        (y_widget1 - y_prev), x_data0, y_data0)
                # update previous positions
                self.p_prev = x_data1, y_data1, x_widget1, y_widget1

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if self.interaction == self.CLICK and e.button() == Qt.MouseButton.LeftButton:
            x0, y0, _, _ = self.p0
            self.set_center_map_view.emit(x0, y0)
            self.interaction = self.INTERACTIVE
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(e)

    def wheelEvent(self, event: QWheelEvent) -> None:
        x, y = self.get_texture_coordinate(int(event.position().x()), int(event.position().y()))
        ds = event.angleDelta().y()/8  # degrees
        self.zoom_map_view.emit(ds, x, y)

    # connected to MapView's viewport_matrix_changed
    @Slot(object)
    def update_mapview_viewport_matrix(self, m: matrix.Matrix) -> None:
        self.mapview_viewport_matrix = m
        self.update()

    def update_view_matrix(self) -> None:
        if self.map_model.tex_width and self.map_model.tex_height:
            # texture size
            tex_w, tex_h = self.map_model.tex_width, self.map_model.tex_height
            self.cx, self.cy = tex_w//2, tex_h//2
            # view size
            view_w, view_h = self.width(), self.height()
            # size ratios
            view_ratio, tex_ratio = view_w / view_h, tex_w / tex_h
            if view_ratio > tex_ratio:
                # view is wider than texture
                # zoom is thus the height ratio between view and texture
                self.z = view_h / tex_h
            else:
                # view is higher than texture
                # zoom is thus the width ratio between view and texture
                self.z = view_w / tex_w
        super().update_view_matrix()
