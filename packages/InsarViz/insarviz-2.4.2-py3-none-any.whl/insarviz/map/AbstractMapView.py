#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" AbstractMapView

This module contains the class AbstractMapView that is a generic widget for
image views. It is inherited by MapView and MinimapView classes
(in the modules named MapView and MinimapView).
"""


# imports ###################################################################

import ctypes

from OpenGL import GL

import numpy as np

from PySide6.QtCore import Qt, Slot, Signal

from PySide6.QtWidgets import QWidget

from PySide6.QtOpenGLWidgets import QOpenGLWidget

from PySide6.QtGui import QMouseEvent, QWheelEvent

from PySide6.QtOpenGL import QOpenGLVertexArrayObject, QOpenGLBuffer

from shiboken6 import VoidPtr

from insarviz.map.MapModel import MapModel

from insarviz.linalg import matrix, vector

if True and False:
    import OpenGL
    OpenGL.ERROR_CHECKING = False
    OpenGL.ERROR_LOGGING = False
    OpenGL.ERROR_ON_COPY = True
    OpenGL.STORE_POINTERS = False

# Abstract map view ###############################################################


class AbstractMapView(QOpenGLWidget):
    """
    Abstract class for a map view, a QOpenGLWidget display of the
    displacement data, color coded using a colormap
    """

    INTERACTIVE: int = 0

    displayed_area_changed = Signal(tuple, tuple, tuple)

    def __init__(self, map_model: MapModel, parent: QWidget):
        """
        Generate AbstractView.

        Parameters
        ----------
        map_model : MapModel
        """
        super().__init__(parent)
        self.map_model: MapModel = map_model
        self.map_model.layer_model.dataChanged.connect(self.paint)
        self.map_model.layer_model.rowsInserted.connect(self.paint)
        self.map_model.layer_model.rowsMoved.connect(self.paint)
        self.map_model.layer_model.rowsRemoved.connect(self.paint)
        self.map_model.request_paint.connect(self.paint)
        self.map_model.request_set_view_center.connect(self.set_view_center)
        self.interaction: int = 0
        self.set_interaction(self.INTERACTIVE)
        self.left_drag: bool = False
        self.right_drag: bool = False
        # OpenGL vertex array object holding a square on which to display texture
        self.vao = QOpenGLVertexArrayObject()
        self.z: float = 1.0  # zoom level
        # center of the view matrix in data coordinates
        self.cx: float = 0.
        self.cy: float = 0.
        self.view_matrix: matrix.Matrix = matrix.identity()
        self.view_matrix_inverse: matrix.Matrix = matrix.identity()
        self.projection_matrix: matrix.Matrix = matrix.identity()
        # position of the last mouse press (xdata, ydata, xwidget, ywidget)
        self.p0: tuple[float, float, int, int] = 0., 0., 0, 0
        # last position of the mouse (xdata, ydata, xwidget, ywidget)
        self.p_prev: tuple[float, float, int, int] = 0., 0., 0, 0

    # opengl

    def initializeGL(self) -> None:
        glfunc = self.context().functions()
        glfunc.glClearColor(0.5, 0.5, 0.5, 1.)
        # build a Vertex Array Object that is a square from (0,0) to (1,1) mapped with a texture
        # also from (0,0) to (1,1). The vertex are given in such order that:
        # glDrawArrays(GL_LINE_LOOP, 0, 4) draws the square's border
        # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None) draws the textured square
        self.vao.create()
        self.vao.bind()
        vertex = np.ravel([
            # vertex_x, vertex_y, vertex_z, texture_x, texture_y
            [0., 0., 0., 0., 0.],
            [1., 0., 0., 1., 0.],
            [1., 1., 0., 1., 1.],
            [0., 1., 0., 0., 1.]
        ]).astype(np.float32)
        vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
        vertex_buffer.create()
        vertex_buffer.setUsagePattern(QOpenGLBuffer.UsagePattern.StaticDraw)
        vertex_buffer.bind()
        vertex_buffer.allocate(bytes(vertex), vertex.nbytes)
        float_size: int = ctypes.sizeof(ctypes.c_float)
        vertex_offset = VoidPtr(0 * float_size)
        tex_coord_offset = VoidPtr(3 * float_size)
        record_len: int = 5 * float_size
        glfunc.glEnableVertexAttribArray(0)
        glfunc.glVertexAttribPointer(0, 3, int(GL.GL_FLOAT), int(GL.GL_FALSE), record_len,
                                     vertex_offset)
        glfunc.glVertexAttribPointer(1, 2, int(GL.GL_FLOAT), int(GL.GL_FALSE), record_len,
                                     tex_coord_offset)
        glfunc.glEnableVertexAttribArray(1)
        indices = np.array([0, 1, 3, 1, 2, 3], dtype='uint32')
        indices_buffer = QOpenGLBuffer(QOpenGLBuffer.Type.IndexBuffer)
        indices_buffer.create()
        indices_buffer.setUsagePattern(QOpenGLBuffer.UsagePattern.StaticDraw)
        indices_buffer.bind()
        indices_buffer.allocate(indices, indices.nbytes)
        self.vao.release()
        vertex_buffer.release()
        indices_buffer.release()

    def resizeGL(self, width: int, height: int) -> None:
        """
        Resize OpenGL view according to new settings

        Parameters
        ----------
        width : int
            new view width.
        height : int
            new view height.
        """
        glfunc = self.context().functions()
        glfunc.glViewport(0, 0, width, height)
        self.update_projection_matrix()
        self.update_view_matrix()

    # interaction
    @Slot(int)
    def set_interaction(self, value: int) -> None:
        self.interaction = value

    @Slot(float, float)
    def set_view_center(self, cx: float, cy: float) -> None:
        self.cx = cx
        self.cy = cy
        self.paint()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        # pylint: disable=missing-function-docstring, invalid-name
        if self.map_model.current_band_index is not None and not self.left_drag and not self.right_drag:
            if e.button() == Qt.MouseButton.LeftButton:
                self.left_drag = True
            elif e.button() == Qt.MouseButton.RightButton:
                self.right_drag = True

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        # pylint: disable=missing-function-docstring, invalid-name
        if self.left_drag and e.button() == Qt.MouseButton.LeftButton:
            self.left_drag = False
        elif self.right_drag and e.button() == Qt.MouseButton.RightButton:
            self.right_drag = False

    def wheelEvent(self, event: QWheelEvent) -> None:
        # pylint: disable=invalid-name
        """
        Update zoom value according to mouse wheel angle change
        """
        x: float
        y: float
        x, y = self.get_texture_coordinate(int(event.position().x()), int(event.position().y()))
        ds: float = event.angleDelta().y()/8  # degrees
        self.zoom(ds, x, y)

    @Slot(float, float, float)
    def zoom(self, ds: float, x: float, y: float) -> None:
        """
        Called by MouseMoveEvent and wheelEvent on Map. Update Map variables
        for display at new zoom level.

        Parameters
        ----------
        ds : float
            zoom change (mouse wheel angle in degrees or right-click+drag distance).
        x : float
            x-axis position of the zoom change focal point.
        y : float
            y-axis position of the zoom change focal point.
        """
        dz: float = np.exp(ds*0.01)
        self.z *= dz
        # for (x,y) to stay at the same position in the view
        # the following equations must be satistied:
        # (x - cx_i) * z = (x - cx_i+1) * z * dz
        # (y - cy_i) * z = (y - cy_i+1) * z * dz
        # (distance of (x,y) from the center of the view shall remain the same after zooming)
        self.cx = x - (x - self.cx) / dz
        self.cy = y - (y - self.cy) / dz
        self.update_view_matrix()
        self.update()

    @Slot(float, float)
    def pan(self, dx: float, dy: float) -> None:
        """
        Move the camera (translation in x/y)
        Parameters
        ----------
        dx : float
            change in Map view position along x-axis.
        dy : float
            change in Map view position along y-axis.
        """
        self.cx += dx
        self.cy += dy
        self.update_view_matrix()
        self.update()

    def get_texture_coordinate(self, x: int, y: int) -> tuple[float, float]:
        """
        Transform screen coord to texture coord.

        Parameters
        ----------
        x : int
        y : int

        Returns
        -------
        tuple (float, float)
            texture coordinates
        """
        screen_coord = vector.matrix((float(x), float(y), 0., 1.))
        texture_coord = matrix.product(self.view_matrix_inverse, screen_coord)
        return texture_coord[0][0], texture_coord[1][0]

    def update_view_matrix(self) -> None:
        flip_matrix = matrix.identity()
        if self.map_model.flip_h:
            flip_matrix = matrix.mul(matrix.scale(sx=-1.), flip_matrix)
            flip_matrix = matrix.mul(matrix.translate(tx=self.width()), flip_matrix)
        if self.map_model.flip_v:
            flip_matrix = matrix.mul(matrix.scale(sy=-1.), flip_matrix)
            flip_matrix = matrix.mul(matrix.translate(ty=self.height()), flip_matrix)
        self.view_matrix = matrix.product(
            flip_matrix,
            matrix.translate(self.width()//2, self.height()//2),
            matrix.scale(self.z, self.z),
            matrix.translate(-self.cx, -self.cy)
        )
        self.view_matrix_inverse = matrix.product(
            matrix.translate(self.cx, self.cy),
            matrix.scale(1./self.z, 1./self.z),
            matrix.translate(-self.width()//2, -self.height()//2),
            flip_matrix
        )
        self.displayed_area_changed.emit(self.get_texture_coordinate(0, 0),
                                         self.get_texture_coordinate(self.width(), self.height()),
                                         (self.width(), self.height()))

    def update_projection_matrix(self) -> None:
        # vertical case is reversed because OpenGl Y axis is flipped with respect to data Y axis
        self.projection_matrix = matrix.ortho(0, self.width(), self.height(), 0, -1, 1)

    @Slot()
    def paint(self) -> None:
        self.update_view_matrix()
        self.update_projection_matrix()
        self.update()
