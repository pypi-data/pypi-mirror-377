# -*- coding: utf-8 -*-

from typing import Any, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, Slot

from PySide6.QtGui import QIcon

from PySide6.QtWidgets import (
    QWidget, QMessageBox, QDialog, QDialogButtonBox, QGridLayout, QLineEdit, QLabel
)

import rasterio

import numpy as np

import pathlib

from owslib.wmts import WebMapTileService

from insarviz.map.layers.TileLayer import TileLayer

if TYPE_CHECKING:
    from insarviz.map.MapModel import MapModel
    from insarviz.map.AbstractMapView import AbstractMapView


# TEST WMTS servers

# self.wmts = WebMapTileService(r'http://tiles.maps.eox.at/wmts')
# self.layer = 'osm_3857'
# self.tilematrixset = 'GoogleMapsCompatible'

# self.wmts = WebMapTileService(r'https://data.geopf.fr/wmts')
# self.layer: str = 'ORTHOIMAGERY.ORTHOPHOTOS'
# self.tilematrixset: str = 'PM_0_21'

class WMTSLayer(TileLayer):

    icon: QIcon = QIcon()
    kind: str = "WMTS layer"

    def __init__(self, name: str, model: "MapModel", map_widget: "AbstractMapView",
                 server: str, layer: str, tilematrixset: str):
        super().__init__(name, model, map_widget)
        if self.icon.isNull():
            # cannot be initialized in the class declaration because:
            # "QIcon needs a QGuiApplication instance before the icon is created." see QIcon doc
            WMTSLayer.icon = QIcon('icons:WMS.svg')
        try:
            self.wmts = WebMapTileService(server)
        except Exception as e:
            QMessageBox.critical(None, "Connection Error",
                                 f"Impossible to connect to {server}.\nIs internet available ?\n\n\nError:\n{repr(e)}")
            raise RuntimeError("Unable to connect to WMTS")
        if layer not in self.wmts.contents:
            QMessageBox.critical(None, "Invalid layer",
                                 f"Layer {layer} not found in {server}.")
            raise KeyError(f"Layer {self.layer} not found in {server}")
        self.layer: str = layer
        if tilematrixset not in self.wmts.contents[self.layer].tilematrixsetlinks.keys():
            QMessageBox.critical(None, "Invalid tilematrix set",
                                 f"Tilematrix set {tilematrixset} not found for layer {layer} in {server}.")
            raise KeyError(
                f"Tilematrix set {tilematrixset} not found for layer {layer} in {server}.")
        self.tilematrixset: str = tilematrixset
        self.format: str
        if "image/jpeg" in self.wmts.contents[self.layer].formats:
            self.format = "image/jpeg"
        elif "image/png" in self.wmts.contents[self.layer].formats:
            self.format = "image/png"
        else:
            QMessageBox.critical(None, "Invalid image format",
                                 f"Wmts does not have jpeg or png formats for the required layer: {self.wmts.contents[self.layer].formats}.")
            raise RuntimeError(
                f"wmts does not have jpeg or png formats: {self.wmts.contents[self.layer].formats}")
        self.crs = rasterio.CRS.from_string(self.wmts.tilematrixsets[self.tilematrixset].crs)
        # some wmts lack operation name, don't know why
        for i, op in enumerate(self.wmts.operations):
            if (not hasattr(op, 'name')):
                self.wmts.operations[i].name = ""
        # to make the computations, the crs unit shall be meters, see https://www.ogc.org/standard/wmts/
        if self.crs.units_factor[0] not in ("metre", "meter"):
            QMessageBox.critical(None, "Incompatible dataset crs",
                                 "In order to use a WMTS layer, the main data crs unit must be 'meter' or 'metre'.")
            raise RuntimeError(
                f"main data crs unit must be 'meter' or 'metre'")
        assert not (rasterio.crs.epsg_treats_as_latlong(self.crs))
        for zoom, tilematrix in self.wmts.tilematrixsets[self.tilematrixset].tilematrix.items():
            # compute the corners of the tilematrix in its crs coordinates
            # see https://www.ogc.org/standard/wmts/
            left, top = tilematrix.topleftcorner
            pixelspan = tilematrix.scaledenominator * 0.00028 * self.crs.units_factor[1]
            right = left + pixelspan * tilematrix.tilewidth * tilematrix.matrixwidth
            bottom = top - pixelspan * tilematrix.tileheight * tilematrix.matrixheight
            # transform into coordinates in the main dataset crs
            left, bottom, right, top = rasterio.warp.transform_bounds(self.crs, self.main_crs,
                                                                      left, bottom, right, top)
            # the antimeridian can have the same value for left and right in some crs
            if np.isclose(left, right):
                left, right = -np.abs(left), np.abs(right)
            # transform into coordinates in main dataset pixels
            left, top = ~self.main_transform * (left, top)
            right, bottom = ~self.main_transform * (right, bottom)
            tile_to_texture_pixelratioX = (right - left) / \
                (tilematrix.tilewidth * tilematrix.matrixwidth)
            tile_to_texture_pixelratioY = (bottom - top) / \
                (tilematrix.tileheight * tilematrix.matrixheight)
            self.tile_to_texture_pixelratio[int(zoom)] = tile_to_texture_pixelratioX
            # np.mean([tile_to_texture_pixelratioX,tile_to_texture_pixelratioY])

    def tilematrix_xy_to_tilematrix_crs(self, zoom: int, x: int, y: int) -> tuple[float, float, float, float]:
        """
        Return the rect of the tile in self.crs coordinates as left, bottom, right, top
        """
        try:
            tilematrix = self.wmts.tilematrixsets[self.tilematrixset].tilematrix[str(zoom)]
        except KeyError:
            raise ValueError(f'zoom {zoom} is not in tilematrixset {self.tilematrixset}')
        if x < 0 or x >= tilematrix.matrixwidth:
            raise ValueError(f"x {x} is < 0 or >= tilematrix.width")
        if y < 0 or y >= tilematrix.matrixheight:
            raise ValueError(f"y {y} is < 0 or >= tilematrix height")
        tilematrixlimits = self.wmts.contents[self.layer].tilematrixsetlinks[self.tilematrixset].tilematrixlimits
        if tilematrixlimits:
            tilematrixlimit = tilematrixlimits[str(zoom)]
            if x < tilematrixlimit.mintilecol or x > tilematrixlimit.maxtilecol:
                raise ValueError(f"x {x} is out of tilematrixlimit")
            if y < tilematrixlimit.mintilerow or y > tilematrixlimit.maxtilerow:
                raise ValueError(f"y {y} is out of tilematrixlimit")
        # compute the corner of the tile xy in its crs coordinates
        pixelspan = tilematrix.scaledenominator * 0.00028 * self.crs.units_factor[1]
        left, top = tilematrix.topleftcorner
        left = left + pixelspan * x * tilematrix.tilewidth
        top = top - pixelspan * y * tilematrix.tileheight
        right = left + pixelspan * tilematrix.tilewidth
        bottom = top - pixelspan * tilematrix.tileheight
        return left, bottom, right, top

    def request_url(self, zoom: int, x: int, y: int) -> str:
        """
        Return the url to request the tile as a string
        """
        request = self.wmts.buildTileRequest(layer=self.layer, tilematrixset=self.tilematrixset,
                                             tilematrix=str(zoom), row=y, column=x,
                                             format=self.format)
        return self.wmts.url + '?' + request

    def tile_shape(self, zoom: int) -> tuple[int, int]:
        """
        Return the shape (width, height) in pixels of a tile at the given zoom level
        """
        try:
            tilematrix = self.wmts.tilematrixsets[self.tilematrixset].tilematrix[str(zoom)]
        except KeyError:
            raise ValueError(f'zoom {zoom} is not in tilematrixset {self.tilematrixset}')
        return (tilematrix.tilewidth, tilematrix.tileheight)

    def main_crs_to_tilematrix_xy(self, left: float, bottom: float, right: float, top: float,
                                  zoom: int) -> tuple[int, int, int, int]:
        """
        Return the rect of tiles in xy coordinates as left, bottom, right, top
        """
        try:
            tilematrix = self.wmts.tilematrixsets[self.tilematrixset].tilematrix[str(zoom)]
        except KeyError:
            raise ValueError(f'zoom {zoom} is not in tilematrixset {self.tilematrixset}')
        # transform into coordinates in the tilematrix crs
        left, bottom, right, top = rasterio.warp.transform_bounds(
            self.main_crs, self.crs, left, bottom, right, top)
        tilematrix_bounds = self.tilematrix_bounds(zoom)
        # if both rects do not intersect return None
        if left > tilematrix_bounds[2]:
            return None
        if bottom > tilematrix_bounds[3]:
            return None
        if right < tilematrix_bounds[0]:
            return None
        if top < tilematrix_bounds[1]:
            return None
        # take the intersection between both rects
        left = max(left, tilematrix_bounds[0])
        bottom = max(bottom, tilematrix_bounds[1])
        right = min(right, tilematrix_bounds[2])
        top = min(top, tilematrix_bounds[3])
        # compute the x and y values
        pixelspan = tilematrix.scaledenominator * 0.00028 * self.crs.units_factor[1]
        left = int((left - tilematrix.topleftcorner[0]) / (pixelspan * tilematrix.tilewidth))
        bottom = int(
            (tilematrix.topleftcorner[1] - bottom) / (pixelspan * tilematrix.tileheight))
        right = int((right - tilematrix.topleftcorner[0]) / (pixelspan * tilematrix.tilewidth))
        top = int((tilematrix.topleftcorner[1] - top) / (pixelspan * tilematrix.tileheight))
        return left, bottom, right, top

    def tilematrix_bounds(self, zoom: int) -> tuple[float, float, float, float]:
        if str(zoom) in self.wmts.tilematrixsets[self.tilematrixset].tilematrix:
            tilematrix = self.wmts.tilematrixsets[self.tilematrixset].tilematrix[str(zoom)]
            pixelspan = tilematrix.scaledenominator * 0.00028 * self.crs.units_factor[1]
            left, top = tilematrix.topleftcorner
            tilematrixlimits = self.wmts.contents[self.layer].tilematrixsetlinks[self.tilematrixset].tilematrixlimits
            if tilematrixlimits:
                tilematrixlimit = tilematrixlimits[str(zoom)]
                left = left + pixelspan * tilematrixlimit.mintilecol * tilematrix.tilewidth
                top = top + pixelspan * tilematrixlimit.mintilerow * tilematrix.tileheight
                right = left + pixelspan * tilematrixlimit.maxtilecol * tilematrix.tilewidth
                bottom = top - pixelspan * tilematrixlimit.maxtilerow * tilematrix.tileheight
            else:
                right = left + pixelspan * tilematrix.matrixwidth * tilematrix.tilewidth
                bottom = top - pixelspan * tilematrix.matrixheight * tilematrix.tileheight
            return left, bottom, right, top
        else:
            raise ValueError(f'zoom {zoom} is not in tilematrixset {self.tilematrixset}')

    def to_dict(self, project_path: pathlib.Path) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict(project_path)
        output["server"] = self.wmts.url
        output["wmts_layer"] = self.layer
        output["tilematrixset"] = self.tilematrixset
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any], map_model: "MapModel",
                  map_widget: "AbstractMapView") -> "WMTSLayer":
        assert input_dict["kind"] == cls.kind
        name = input_dict.get("name", "WMTS layer")
        server = input_dict["server"]
        layer = input_dict["wmts_layer"]
        tilematrixset = input_dict["tilematrixset"]
        layer = WMTSLayer(name, map_model, map_widget, server, layer, tilematrixset)
        if "visible" in input_dict:
            layer.visible = input_dict["visible"]
        if "alpha" in input_dict:
            layer.alpha = input_dict["alpha"]
        return layer


class WMTSLayerDialog(QDialog):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setModal(True)
        self.setWindowTitle("Create WMTS Layer")
        # labels
        self.server_label = QLabel("Server url:")
        self.layer_label = QLabel("Layer:")
        self.tilematrixset_label = QLabel("Tilematrix set:")
        # inputs
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://...")
        self.server_input.textChanged.connect(self.test_enable_ok)
        self.layer_input = QLineEdit()
        self.layer_input.setPlaceholderText("Layer name")
        self.layer_input.textChanged.connect(self.test_enable_ok)
        self.tilematrixset_input = QLineEdit()
        self.tilematrixset_input.setPlaceholderText("Tilematrix set name")
        self.tilematrixset_input.textChanged.connect(self.test_enable_ok)
        # buttons
        self.button_box = QDialogButtonBox()
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.clicked.connect(self.accept)
        # main layout
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.server_label, 0, 0)
        self.main_layout.addWidget(self.server_input, 0, 1)
        self.main_layout.addWidget(self.layer_label, 1, 0)
        self.main_layout.addWidget(self.layer_input, 1, 1)
        self.main_layout.addWidget(self.tilematrixset_label, 2, 0)
        self.main_layout.addWidget(self.tilematrixset_input, 2, 1)
        self.main_layout.addWidget(self.button_box, 3, 0, 1, 2)
        self.setLayout(self.main_layout)
        self.test_enable_ok()

    @Slot()
    def test_enable_ok(self) -> None:
        enable_ok = True
        if self.server_input.text() == "":
            enable_ok = False
        if self.layer_input.text() == "":
            enable_ok = False
        if self.tilematrixset_input.text() == "":
            enable_ok = False
        self.ok_button.setEnabled(enable_ok)

    def sizeHint(self) -> QSize:
        return QSize(512, super().sizeHint().height())
