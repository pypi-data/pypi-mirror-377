# -*- coding: utf-8 -*-

from typing import Any, Optional, Union, TYPE_CHECKING

import logging

import warnings

from collections import OrderedDict

import asyncio
import aiohttp

from PySide6.QtCore import Slot, Signal

from PySide6.QtWidgets import QApplication

from PySide6.QtGui import QPainter, QMatrix4x4

from PySide6.QtOpenGL import (
    QOpenGLShader, QOpenGLTexture, QAbstractOpenGLFunctions, QOpenGLVertexArrayObject
)

from qasync import asyncSlot

from shiboken6 import VoidPtr

from OpenGL import GL

import numpy as np

import rasterio

from insarviz.map.layers.Layer import OpenGLLayer

from insarviz.map.Shaders import VERT_SHADER, ALPHA_SHADER, IMAGE_RGB_SHADER

from insarviz.linalg import matrix

import insarviz.version

if TYPE_CHECKING:
    from insarviz.map.MapModel import MapModel
    from insarviz.map.AbstractMapView import AbstractMapView

logger = logging.getLogger(__name__)


class TileLayer(OpenGLLayer):
    """
    Abstract class
    """

    tiles_cache_size: int = 100
    # user agent required for OpenStreetMap https://operations.osmfoundation.org/policies/tiles/
    http_headers = {
        "User-Agent": f"InsarViz/{insarviz.version.__version__} aiohttp/{aiohttp.__version__}"}

    def __init__(self, name: str, model: "MapModel", map_widget: "AbstractMapView"):
        super().__init__(name)
        self.main_transform = model.loader.dataset.transform
        self.main_crs = model.loader.dataset.crs
        map_widget.displayed_area_changed.connect(self.update_tileset)
        # implements a max_sized FIFO cache, keys are (zoom, x, y)
        self.tiles: OrderedDict[tuple[int, int, int], asyncio.Task] = OrderedDict()
        self.tiles_cache_size = 100
        self.zoom: int = 0
        # dictionnary linking zoom level to pixel ratio from tile to main dataset texture ?
        self.tile_to_texture_pixelratio: dict[int, float] = {}
        self.left_tile: int = 0
        self.right_tile: int = 0
        self.top_tile: int = 0
        self.bottom_tile: int = 0
        self.http_session = aiohttp.ClientSession(headers=TileLayer.http_headers)
        self.crs: rasterio.crs.CRS

    def tile_shape(self, zoom: int) -> tuple[int, int]:
        """
        Return the shape (width, height) in pixels of a tile at the given zoom level
        """
        raise NotImplementedError

    def tilematrix_xy_to_tilematrix_crs(self, zoom: int, x: int, y: int) -> tuple[float, float, float, float]:
        """
        Return the rect of the tile in self.crs coordinates as left, bottom, right, top
        """
        raise NotImplementedError

    def main_crs_to_tilematrix_xy(self, left: float, bottom: float, right: float, top: float,
                                  zoom: int) -> tuple[int, int, int, int]:
        """
        Return the rect of tiles in xy coordinates as left, bottom, right, top
        """
        raise NotImplementedError

    def request_url(self, zoom: int, x: int, y: int) -> str:
        """
        Return the url to request the tile as a string
        """
        raise NotImplementedError

    # connected to MapView.displayed_area_changed
    @asyncSlot(tuple, tuple, tuple)
    async def update_tileset(self, top_left: tuple[float, float], bottom_right: tuple[float, float],
                             shape: tuple[int, int]) -> None:
        """
        _summary_

        Parameters
        ----------
        top_left : tuple[float, float]
            coordinates of the top left corner of MapView in texture coordinates of the data set
        bottom_right :tuple[float, float]
            coordinates of the bottom right corner of MapView in texture coordinates of the data set
        shape : tuple[int, int]
            shape of map view (width, height) in pixels
        """
        screen_to_texture_pixelratio = (np.abs(bottom_right[0] - top_left[0])) / shape[0]
        # set zoom to the nearest zoom in the tilematrix
        self.zoom = min(self.tile_to_texture_pixelratio,
                        key=lambda i: np.abs(screen_to_texture_pixelratio -
                                             self.tile_to_texture_pixelratio.get(i)))
        # transform into x,y tile coordinates
        [left, right], [top, bottom] = rasterio.transform.xy(self.main_transform,
                                                             [top_left[1], bottom_right[1]],
                                                             [top_left[0], bottom_right[0]])
        left, right = min(left, right), max(left, right)
        bottom, top = min(top, bottom), max(top, bottom)
        self.left_tile, self.bottom_tile, self.right_tile, self.top_tile = self.main_crs_to_tilematrix_xy(
            left, bottom, right, top, self.zoom)
        tile_list = []
        for i in range(self.left_tile, self.right_tile+1):
            for j in range(self.top_tile, self.bottom_tile+1):
                if (self.zoom, i, j) in self.tiles:
                    # put the tile at the beginning of the cache if already in here (so it is not
                    # removed when adding the missing tiles)
                    self.tiles.move_to_end((self.zoom, i, j), last=True)
                else:
                    tile_list.append((self.zoom, i, j))
        while len(self.tiles) > self.tiles_cache_size:
            removed = self.tiles.popitem(last=False)
            if removed[1].done() and not removed[1].cancelled():
                if self.context.isValid() and self.offscreen_surface.isValid():
                    self.context.makeCurrent(self.offscreen_surface)
                    # delete the OpenGL textures
                    removed[1].result()[0].destroy()
                    self.context.doneCurrent()
            elif not removed[1].done():
                removed[1].cancel()
        if len(tile_list) > 0:
            for tile in tile_list:
                self.tiles[tile] = asyncio.create_task(self.add_tile(*tile))
            try:
                await asyncio.gather(*[self.tiles[tile] for tile in tile_list])
            except asyncio.CancelledError:
                pass
            self.request_paint.emit()

    async def add_tile(self, zoom: int, x: int, y: int):
        try:
            url = self.request_url(zoom, x, y)
            async with self.http_session.get(url) as resp:
                if resp.status != 200:
                    logger.info(f"HTTP request for tile {url} got {resp.status} status code, abort")
                    return
                tile = await resp.read()
            with warnings.catch_warnings():
                # ignore RuntimeWarning for not georeferenced file
                warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning,
                                        message=("Dataset has no geotransform, gcps, or rpcs. "
                                                 "The identity matrix will be returned."))
                with rasterio.MemoryFile(tile) as notgeo_tile:
                    with notgeo_tile.open() as src:
                        profile = src.profile
                        if src.count in (3, 4):
                            data = src.read([1, 2, 3])
                        elif src.count == 1:
                            # then maybe the tile is one band with a colormap
                            # idea from https://gis.stackexchange.com/questions/377815/cannot-get-color-plot-of-single-band-tiff-image-with-rasterio
                            try:
                                src.colormap(1)
                            except ValueError:
                                logger.info(f"unsupported format for tile {url}")
                                return
                            # transform the colormap into an array
                            colormap = np.asarray([src.colormap(1).get(i, [0, 0, 0, 0]) for i in range(256)],
                                                  dtype=np.uint8)
                            # reconstruct the data into 3 bands rgb using the colormap
                            data = np.transpose(colormap[src.read(1)][:, :, :3], [2, 0, 1]).copy()
                        else:
                            logger.info(f"unsupported format for tile {url}")
                            return
            tile_width, tile_height = self.tile_shape(zoom)
            left, bottom, right, top = self.tilematrix_xy_to_tilematrix_crs(zoom, x, y)
            transform = rasterio.transform.from_bounds(left, bottom, right, top,
                                                       tile_width, tile_height)
            # TODO which compression to use ?
            profile.update(transform=transform, driver='GTiff', crs=self.crs, compress='lzw',
                           width=tile_width, height=tile_height, count=3)
            if "photometric" in profile:
                del profile["photometric"]
            with rasterio.MemoryFile() as geo_tile:
                with geo_tile.open(**profile) as dataset:
                    dataset.write(data)
                with geo_tile.open() as src:
                    with rasterio.vrt.WarpedVRT(src, crs=self.main_crs) as vrt:
                        img = vrt.read()
                        if img.dtype == "uint8":
                            img = img.astype(np.float32)/255
                        # transpose to change shape from (bands, rows, columns) to (rows, columns, bands)
                        # copy to ensure numpy does not create a view (that opengl cannot read properly)
                        img = np.transpose(img, [1, 2, 0]).copy().astype(np.float32)
                        # model matrix transforms coordinates inside the square (0,1) to coordinates in
                        # pixels relatively to the dataset
                        tile_model_matrix = matrix.from_rasterio_Affine(
                            ~self.main_transform
                            * vrt.transform
                            * rasterio.Affine.scale(*vrt.shape[::-1]))
                        h, w, d = img.shape
                        self.context.makeCurrent(self.offscreen_surface)
                        texture = QOpenGLTexture(QOpenGLTexture.Target.Target2D)
                        texture.setMagnificationFilter(QOpenGLTexture.Filter.Linear)
                        texture.setMinificationFilter(QOpenGLTexture.Filter.LinearMipMapLinear)
                        texture.setWrapMode(QOpenGLTexture.WrapMode.ClampToEdge)
                        texture.setSize(w, h)
                        texture.setFormat(QOpenGLTexture.TextureFormat.RGB32F)
                        texture.allocateStorage(QOpenGLTexture.PixelFormat.RGB,
                                                QOpenGLTexture.PixelType.Float32)
                        texture.setData(QOpenGLTexture.PixelFormat.RGB,
                                        QOpenGLTexture.PixelType.Float32, img.data)
                        texture.generateMipMaps()
                        self.context.doneCurrent()
                        assert texture.textureId(
                        ) != 0, f"TileLayer {self.name} cannot load image texture in OpenGl"
            return (texture, tile_model_matrix)
        except asyncio.CancelledError:
            try:
                texture
                self.context.makeCurrent(self.offscreen_surface)
                texture.destroy()
                self.context.doneCurrent()
            except UnboundLocalError:
                # texture does not exist
                pass
            raise

    def show(self, view_matrix: matrix.Matrix, projection_matrix: matrix.Matrix, show_params: OpenGLLayer.ShowParams,
             painter: Optional[QPainter] = None, vao: Optional[QOpenGLVertexArrayObject] = None,
             glfunc: Optional[QAbstractOpenGLFunctions] = None, blend: bool = True) -> None:
        if painter is not None:
            painter.beginNativePainting()
            # a VAO is required because QPainter bound its own VAO so we need to bind back our own
            assert vao is not None, "OpenGLLayer: vao is required when using QPainter"
        if blend:
            glfunc.glEnable(GL.GL_BLEND)
            glfunc.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        if vao is not None:
            vao.bind()
        self.program.bind()
        for i in range(self.left_tile, self.right_tile+1):
            for j in range(self.top_tile, self.bottom_tile+1):
                if self.tiles.get((self.zoom, i, j), None) is not None:
                    tile = self.tiles.get((self.zoom, i, j))
                    if tile.done() and not tile.cancelled() and not tile.exception():
                        texture, model_matrix = tile.result()
                        # bind textures to texture units
                        glfunc.glActiveTexture(GL.GL_TEXTURE0)
                        texture.bind()
                        # set model, view and projection matrixes
                        self.program.setUniformValue(self.program.uniformLocation('model_matrix'),
                                                     QMatrix4x4(matrix.flatten(model_matrix)))
                        self.program.setUniformValue(self.program.uniformLocation('view_matrix'),
                                                     QMatrix4x4(matrix.flatten(view_matrix)))
                        self.program.setUniformValue(self.program.uniformLocation('projection_matrix'),
                                                     QMatrix4x4(matrix.flatten(projection_matrix)))
                        # set alpha value
                        self.program.setUniformValue1f(self.program.uniformLocation('alpha'),
                                                       self.alpha)
                        # draw the two triangles of the VAO that form a square
                        glfunc.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, VoidPtr(0))
                        texture.release()
                elif self.tiles.get((self.zoom-1, i//2, j//2), None) is not None:
                    pass  # TODO
                else:
                    for k in range(2):
                        for l in range(2):
                            if self.tiles.get((self.zoom+1, 2*i+k, 2*j+l), None) is not None:
                                tile = self.tiles.get((self.zoom+1, 2*i+k, 2*j+l))
                                if tile.done() and not tile.cancelled() and not tile.exception():
                                    texture, model_matrix = tile.result()
                                    # bind textures to texture units
                                    glfunc.glActiveTexture(GL.GL_TEXTURE0)
                                    texture.bind()
                                    # set model, view and projection matrixes
                                    self.program.setUniformValue(self.program.uniformLocation('model_matrix'),
                                                                 QMatrix4x4(matrix.flatten(model_matrix)))
                                    self.program.setUniformValue(self.program.uniformLocation('view_matrix'),
                                                                 QMatrix4x4(matrix.flatten(view_matrix)))
                                    self.program.setUniformValue(self.program.uniformLocation('projection_matrix'),
                                                                 QMatrix4x4(matrix.flatten(projection_matrix)))
                                    # set alpha value
                                    self.program.setUniformValue1f(self.program.uniformLocation('alpha'),
                                                                   self.alpha)
                                    # draw the two triangles of the VAO that form a square
                                    glfunc.glDrawElements(GL.GL_TRIANGLES, 6,
                                                          GL.GL_UNSIGNED_INT, VoidPtr(0))
                                    texture.release()
        self.program.release()
        if vao is not None:
            vao.release()
        if painter is not None:
            painter.endNativePainting()

    def build_program(self) -> None:
        self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, VERT_SHADER)
        self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, ALPHA_SHADER)
        self.program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, IMAGE_RGB_SHADER)
        self.program.link()
        self.program.bind()
        self.program.setUniformValue1i(self.program.uniformLocation('image'), 0)
        self.program.release()

    def __del__(self):
        """
        Free textures and shader program from the VRAM when the layer is destroyed to prevent
        memory leaks.
        """
        f = asyncio.create_task(self.http_session.close())
        while not f.done():
            QApplication.instance().processEvents()
        try:
            if self.context.isValid() and self.offscreen_surface.isValid():
                self.context.makeCurrent(self.offscreen_surface)
                # delete the OpenGL textures
                for tile in self.tiles.values():
                    if tile.done() and not tile.cancelled():
                        tile.result()[0].destroy()
                # delete the OpenGL shaders program
                del self.program
                self.context.doneCurrent()
        except RuntimeError:
            # the context has already been deleted
            pass
