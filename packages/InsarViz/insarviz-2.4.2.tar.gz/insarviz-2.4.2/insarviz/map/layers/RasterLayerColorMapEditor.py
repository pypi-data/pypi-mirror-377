# -*- coding: utf-8 -*-

from typing import Optional

import logging

from OpenGL import GL

from PySide6.QtCore import Qt, QSize

from PySide6.QtWidgets import (
    QDialog, QWidget, QDialogButtonBox, QVBoxLayout, QSplitter, QSizePolicy
)

from PySide6.QtOpenGLWidgets import QOpenGLWidget

from PySide6.QtGui import QMatrix4x4

from PySide6.QtOpenGL import QOpenGLVertexArrayObject, QOpenGLShaderProgram, QOpenGLTexture

from shiboken6 import VoidPtr

from pyqtgraph import BarGraphItem

from pyqtgraph.colormap import ColorMap

import numpy as np

from insarviz.colormaps import create_colormap_texture

from insarviz.map.Shaders import DATA_UNIT, COLORMAP_UNIT

from insarviz.map.layers.Layer import Raster1BLayer

from insarviz.ColormapWidget import ColormapWidget, myHistogramWidget

from insarviz.linalg import matrix

from insarviz.map.AbstractMapView import AbstractMapView

logger = logging.getLogger(__name__)


class RasterLayerColorMapEditor(QDialog):

    default_padding = ColormapWidget.default_padding
    max_padding = ColormapWidget.max_padding
    autorange_threshold = ColormapWidget.autorange_threshold

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setModal(True)
        self.setWindowTitle("Edit colormap")
        self.setSizeGripEnabled(True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        self.colormap: Optional[ColorMap] = None

        self.histogram_widget = myHistogramWidget()
        # store the colormap itself because its name is not saved in gradient
        self.histogram_widget.gradient.menu.sigColorMapTriggered.connect(
            self.store_colormap)
        # new histogram curve
        self.hist_plot = BarGraphItem(x0=[], x1=[], y0=[], y1=[],
                                      pen=None, brush=(220, 20, 20, 100))
        self.hist_plot.setZValue(10)
        self.hist_plot.setRotation(90)
        self.histogram_widget.vb.addItem(self.hist_plot)

        self.layer_view = RasterLayerView()
        self.histogram_widget.sigLevelsChanged.connect(self.on_levels_changed)
        self.histogram_widget.gradient.menu.sigColorMapTriggered.connect(
            self.layer_view.set_colormap)

        self.button_box = QDialogButtonBox()
        self.autorange_button = self.button_box.addButton("Autorange",
                                                          QDialogButtonBox.ButtonRole.ResetRole)
        self.autorange_button.clicked.connect(self.autorange)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Apply)
        self.apply_button.clicked.connect(self.accept)

        self.main_widget = QSplitter(Qt.Orientation.Horizontal)
        self.main_widget.setChildrenCollapsible(False)
        self.main_widget.addWidget(self.layer_view)
        self.main_widget.addWidget(self.histogram_widget)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.main_widget)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

    def set_layer(self, layer: Raster1BLayer):
        assert isinstance(layer, Raster1BLayer)
        self.layer_view.set_texture(layer.textures[GL.GL_TEXTURE0+DATA_UNIT], layer.model_matrix)
        self.histogram_widget.setLevels(layer.colormap_v0, layer.colormap_v1)
        self.set_colormap(layer.colormap.name)
        hist, bins = layer.histogram
        self.hist_plot.setOpts(x0=bins[:-1], x1=bins[1:], y0=np.zeros(len(hist)), y1=hist)
        ymin = float(bins[0] - (bins[-1] - bins[0]) * self.max_padding)
        ymax = float(bins[-1] + (bins[-1] - bins[0]) * self.max_padding)
        self.histogram_widget.vb.setLimits(yMin=ymin, yMax=ymax)
        self.histogram_widget.vb.setYRange(bins[1], bins[-2], padding=self.default_padding)

    def on_levels_changed(self) -> None:
        self.layer_view.set_v0_v1(*self.histogram_widget.getLevels())

    def get_v0_v1(self) -> tuple[float, float]:
        return self.histogram_widget.getLevels()

    def autorange(self) -> None:
        hist = self.hist_plot.opts.get('y1')
        bins = np.empty(len(hist)+1)
        bins[:-1] = self.hist_plot.opts.get('x0')
        bins[-1] = self.hist_plot.opts.get('x1')[-1]
        v0, v1 = self.autorange_from_hist(hist, bins)
        self.histogram_widget.setLevels(v0, v1)

    autorange_from_hist = ColormapWidget.autorange_from_hist

    set_colormap = ColormapWidget.set_colormap

    def store_colormap(self, cmap: ColorMap) -> None:
        self.colormap = cmap

    def get_colormap(self) -> ColorMap:
        return self.colormap

    def set_default_colormap(self) -> None:
        # greyscale is the first colormap action (see colormaps.py)
        self.histogram_widget.gradient.menu.actions()[0].trigger()


class RasterLayerView(QOpenGLWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setMinimumSize(QSize(640, 480))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.texture = QOpenGLTexture(QOpenGLTexture.Target.Target2D)
        self.colormap_v0: float = 0.
        self.colormap_v1: float = 1.
        self.colormap_texture = QOpenGLTexture(QOpenGLTexture.Target.Target1D)
        self.program: QOpenGLShaderProgram
        # OpenGL vertex array object holding a square on which to display texture
        self.vao = QOpenGLVertexArrayObject()
        self.z: float = 1.0  # zoom level
        # center of the view matrix in data coordinates
        self.cx: float = 0.
        self.cy: float = 0.
        self.model_matrix: matrix.Matrix = matrix.identity()
        self.view_matrix: matrix.Matrix = matrix.identity()
        self.projection_matrix: matrix.Matrix = matrix.identity()

    def initializeGL(self) -> None:
        AbstractMapView.initializeGL(self)
        self.program = QOpenGLShaderProgram()
        Raster1BLayer.build_program(self)

    resizeGL = AbstractMapView.resizeGL

    def paintGL(self) -> None:
        """
        Generate and display OpenGL texture for Map.
        """
        glfunc = self.context().functions()
        glfunc.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.vao.bind()
        # bind textures to texture units
        glfunc.glActiveTexture(GL.GL_TEXTURE0+DATA_UNIT)
        self.texture.bind()
        glfunc.glActiveTexture(GL.GL_TEXTURE0+COLORMAP_UNIT)
        self.colormap_texture.bind()
        self.program.bind()
        # set view and projection matrixes
        self.program.setUniformValue(self.program.uniformLocation('model_matrix'),
                                     QMatrix4x4(matrix.flatten(self.model_matrix)))
        self.program.setUniformValue(self.program.uniformLocation('view_matrix'),
                                     QMatrix4x4(matrix.flatten(self.view_matrix)))
        self.program.setUniformValue(self.program.uniformLocation('projection_matrix'),
                                     QMatrix4x4(matrix.flatten(self.projection_matrix)))
        self.program.setUniformValue1f(self.program.uniformLocation('v0'), float(self.colormap_v0))
        self.program.setUniformValue1f(self.program.uniformLocation('v1'), float(self.colormap_v1))
        # draw the two triangles of the VAO that form a square
        glfunc.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, VoidPtr(0))
        self.vao.release()
        self.texture.release()
        self.colormap_texture.release()
        self.program.release()

    def update_view_matrix(self) -> None:
        # texture size
        tex_w, tex_h = self.model_matrix[0][0], self.model_matrix[1][1]
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
        self.view_matrix = matrix.product(
            matrix.translate(self.width()//2, self.height()//2),
            matrix.scale(self.z, self.z),
            matrix.translate(-self.cx, -self.cy)
        )

    update_projection_matrix = AbstractMapView.update_projection_matrix

    def set_texture(self, texture: QOpenGLTexture, model_matrix: matrix.Matrix) -> None:
        self.texture = texture
        self.model_matrix = matrix.scale(model_matrix[0][0], model_matrix[1][1])

    def set_v0_v1(self, v0: float, v1: float) -> None:
        self.colormap_v0 = float(v0)
        self.colormap_v1 = float(v1)
        self.repaint()

    def set_colormap(self, colormap: ColorMap) -> None:
        self.makeCurrent()
        self.colormap_texture.destroy()
        self.colormap_texture = create_colormap_texture(colormap)
        self.doneCurrent()
        self.repaint()
