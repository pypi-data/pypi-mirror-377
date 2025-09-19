# -*- coding: utf-8 -*-

from typing import Any, Union, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, QSignalBlocker, Slot

from PySide6.QtGui import QIcon

from PySide6.QtWidgets import (
    QWidget, QSpinBox, QDialog, QDialogButtonBox, QGridLayout, QLineEdit, QLabel, QCompleter,
    QGroupBox, QHBoxLayout
)

import rasterio

import numpy as np

import pathlib

import xyzservices as xyz

from insarviz.map.layers.Layer import OpenGLLayer

from insarviz.map.layers.TileLayer import TileLayer

if TYPE_CHECKING:
    from insarviz.map.MapModel import MapModel
    from insarviz.map.AbstractMapView import AbstractMapView


class XYZLayer(TileLayer):

    icon: QIcon = QIcon()
    kind: str = "XYZ layer"

    def __init__(self, name: str, model: "MapModel", map_widget: "AbstractMapView", provider: xyz.TileProvider):
        super().__init__(name, model, map_widget)
        if self.icon.isNull():
            # cannot be initialized in the class declaration because:
            # "QIcon needs a QGuiApplication instance before the icon is created." see QIcon doc
            XYZLayer.icon = QIcon('icons:WMS.svg')
        self.crs = rasterio.crs.CRS.from_epsg(4326)
        self.provider = provider
        if "max_zoom" not in self.provider:
            self.provider["max_zoom"] = 18
        # TODO test the tile size and that the server responds, otherwise raise Exception
        for i in range(0, self.provider.max_zoom+1):
            # transform the corners of the tilematrix into the main data set crs
            left, bottom, right, top = rasterio.warp.transform_bounds(self.crs, self.main_crs,
                                                                      -180, -85.0511, 180, 85.0511)
            # transform into coordinates in main dataset pixels
            left, top = ~self.main_transform * (left, top)
            right, bottom = ~self.main_transform * (right, bottom)
            tile_to_texture_pixelratioX = (right - left) / (256 * np.power(2, i))
            tile_to_texture_pixelratioY = (bottom - top) / (256 * np.power(2, i))
            self.tile_to_texture_pixelratio[i] = tile_to_texture_pixelratioX

    def request_url(self, zoom: int, x: int, y: int) -> str:
        """
        Return the url to request the tile as a string
        """
        return self.provider.build_url(z=zoom, x=x, y=y)

    def tile_shape(self, zoom: int) -> tuple[int, int]:
        """
        Return the shape (width, height) in pixels of a tile at the given zoom level
        """
        return (256, 256)

    def tilematrix_xy_to_tilematrix_crs(self, zoom: int, x: int, y: int) -> tuple[float, float, float, float]:
        """
        Return the rect of the tile in self.crs coordinates as left, bottom, right, top
        """
        if zoom < 0 or zoom > self.provider.max_zoom:
            raise ValueError(f'zoom {zoom} is < 0 or > {self.provider.max_zoom} max provider zoom')
        if x < 0 or x >= int(np.power(2, zoom)):
            raise ValueError(f'x {x} is < 0 or >= 2^zoom = {int(np.power(2, zoom))}')
        if y < 0 or y >= int(np.power(2, zoom)):
            raise ValueError(f'y {y} is < 0 or >= 2^zoom = {int(np.power(2, zoom))}')
        left, right = x_to_long([x, x+1], zoom)
        top, bottom = y_to_lat([y, y+1], zoom)
        return left, bottom, right, top

    def main_crs_to_tilematrix_xy(self, left: float, bottom: float, right: float, top: float,
                                  zoom: int) -> tuple[int, int, int, int]:
        """
        Return the rect of tiles in xy coordinates as left, bottom, right, top
        """
        if zoom < 0 or zoom > self.provider.max_zoom:
            raise ValueError(f'zoom {zoom} is < 0 or > {self.provider.max_zoom} max provider zoom')
        # transform into coordinates in the tilematrix crs (long lat)
        left, bottom, right, top = rasterio.warp.transform_bounds(self.main_crs, self.crs,
                                                                  left, bottom, right, top)
        left, right = long_to_x([left, right], zoom)
        top, bottom = lat_to_y([top, bottom], zoom)
        return left, bottom, right, top

    def to_dict(self, project_path: pathlib.Path) -> dict[str, Any]:
        output: dict[str, Any] = super().to_dict(project_path)
        output["provider"] = dict(self.provider)
        return output

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any], map_model: "MapModel", map_widget: "AbstractMapView") -> "XYZLayer":
        assert input_dict["kind"] == cls.kind
        name = input_dict.get("name", "XYZ layer")
        try:
            provider = xyz.providers.flatten()[input_dict["provider"]["name"]]
        except:
            provider = xyz.TileProvider(input_dict["provider"])
        layer = XYZLayer(name, map_model, map_widget, provider)
        if "visible" in input_dict:
            layer.visible = input_dict["visible"]
        if "alpha" in input_dict:
            layer.alpha = input_dict["alpha"]
        return layer


def long_to_x(long: Union[float, list[float]], zoom: int) -> Union[int, list[int]]:
    # see https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Mathematics
    if isinstance(long, (int, float)):
        result = int(np.floor(np.power(2, zoom) * (long + 180.0) / 360.0))
        return min(np.power(2, zoom) - 1, max(0, result))
    return [long_to_x(_, zoom) for _ in long]


def x_to_long(x: Union[int, list[int]], zoom: int) -> Union[float, list[float]]:
    # see https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Mathematics
    if isinstance(x, (int)):
        return x / np.power(2, zoom) * 360.0 - 180.0
    return [x_to_long(_, zoom) for _ in x]


def lat_to_y(lat: Union[float, list[float]], zoom: int) -> Union[int, list[int]]:
    # see https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Mathematics
    if isinstance(lat, (int, float)):
        result = int(np.floor(np.power(2, zoom) *
                              (1.0 - np.asinh(np.tan(np.radians(lat))) / np.pi) / 2.0))
        return min(np.power(2, zoom) - 1, max(0, result))
    return [lat_to_y(_, zoom) for _ in lat]


def y_to_lat(y: Union[int, list[int]], zoom: int) -> Union[float, list[float]]:
    # see https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Mathematics
    if isinstance(y, (int)):
        return np.degrees(np.atan(np.sinh(np.pi * (1 - 2 * y / np.power(2, zoom)))))
    return [y_to_lat(_, zoom) for _ in y]


class OpenStreetMapLayer(XYZLayer):

    kind = "OpenStreetMap Layer"

    def __init__(self, model: "MapModel", map_widget: "AbstractMapView", name: str = "OpenStreetMap"):
        super().__init__(name, model, map_widget, xyz.providers.OpenStreetMap.Mapnik)

    to_dict = OpenGLLayer.to_dict

    @classmethod
    def from_dict(cls, input_dict: dict[str, Any], map_model: "MapModel", map_widget: "AbstractMapView") -> "OpenStreetMapLayer":
        assert input_dict["kind"] == cls.kind
        name = input_dict.get("name", "OpenStreetMap")
        layer = OpenStreetMapLayer(map_model, map_widget, name=name)
        if "visible" in input_dict:
            layer.visible = input_dict["visible"]
        if "alpha" in input_dict:
            layer.alpha = input_dict["alpha"]
        return layer


class XYZLayerDialog(QDialog):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.provider: Optional[xyz.lib.TileProvider] = None
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setModal(True)
        self.setWindowTitle("Create XYZ Layer")
        # labels
        self.provider_label = QLabel("Provider:")
        self.url_label = QLabel("URL:")
        self.min_zoom_label = QLabel("Min Zoom level:")
        self.max_zoom_label = QLabel("Max Zoom level:")
        # inputs
        self.provider_input = QLineEdit("Custom")
        completer_list = list(xyz.providers.flatten().keys())
        completer_list.append("Custom")
        self.provider_completer = QCompleter(completer_list)
        self.provider_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.provider_input.setCompleter(self.provider_completer)
        self.provider_input.textChanged.connect(self.set_provider)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(r"http://example.com/{z}/{x}/{y}.png")
        self.url_input.textChanged.connect(self.set_custom)
        self.min_zoom_input = QSpinBox()
        self.min_zoom_input.setMinimum(0)
        self.min_zoom_input.valueChanged.connect(self.set_custom)
        self.max_zoom_input = QSpinBox()
        self.max_zoom_input.setMinimum(0)
        self.max_zoom_input.valueChanged.connect(self.set_custom)
        self.api_key_groupbox = QGroupBox("Authentication")
        self.api_key_label = QLabel("Api Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.textChanged.connect(self.test_enable_ok)
        self.api_key_layout = QHBoxLayout()
        self.api_key_layout.addWidget(self.api_key_label)
        self.api_key_layout.addWidget(self.api_key_input)
        self.api_key_groupbox.setLayout(self.api_key_layout)
        self.api_key_groupbox.setCheckable(True)
        self.api_key_groupbox.setChecked(False)
        self.api_key_groupbox.clicked.connect(self.set_custom)
        # buttons
        self.button_box = QDialogButtonBox()
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.clicked.connect(self.accept)
        # main layout
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.provider_label, 0, 0)
        self.main_layout.addWidget(self.provider_input, 0, 1)
        self.main_layout.addWidget(self.url_label, 1, 0)
        self.main_layout.addWidget(self.url_input, 1, 1)
        self.main_layout.addWidget(self.min_zoom_label, 2, 0)
        self.main_layout.addWidget(self.min_zoom_input, 2, 1)
        self.main_layout.addWidget(self.max_zoom_label, 3, 0)
        self.main_layout.addWidget(self.max_zoom_input, 3, 1)
        self.main_layout.addWidget(self.api_key_groupbox, 4, 0, 1, 2)
        self.main_layout.addWidget(self.button_box, 5, 0, 1, 2)
        self.setLayout(self.main_layout)
        self.test_enable_ok()

    @Slot(str)
    def set_provider(self, provider_name: str) -> None:
        providers = xyz.providers.flatten()
        if provider_name in providers.keys():
            self.provider = providers[provider_name]
            # QSignalBlocker to prevent valueChanged signals from being fired
            with QSignalBlocker(self.url_input):
                self.url_input.setText(self.provider["url"])
            with QSignalBlocker(self.min_zoom_input):
                self.min_zoom_input.setValue(self.provider.get("min_zoom", 0))
            with QSignalBlocker(self.max_zoom_input):
                self.max_zoom_input.setValue(self.provider.get("max_zoom", 18))
            self.api_key_input.setText("")
            with QSignalBlocker(self.api_key_groupbox):
                if self.provider.requires_token():
                    self.api_key_groupbox.setChecked(True)
                else:
                    self.api_key_groupbox.setChecked(False)
            self.test_enable_ok()
        elif self.provider is not None:
            self.set_custom()

    @Slot()
    def set_custom(self) -> None:
        self.provider = None
        self.provider_input.setText("Custom")
        self.test_enable_ok()

    @Slot()
    def test_enable_ok(self) -> None:
        enable_ok = True
        if self.min_zoom_input.value() > self.max_zoom_input.value():
            enable_ok = False
        if self.provider is not None:
            if self.provider.requires_token():
                if self.api_key_input.text() == "" or not self.api_key_groupbox.isChecked():
                    enable_ok = False
        else:
            if self.url_input.text() == "":
                enable_ok = False
            if self.api_key_groupbox.isChecked() and self.api_key_input.text() == "":
                enable_ok = False
        self.ok_button.setEnabled(enable_ok)

    def accept(self) -> None:
        if self.provider is not None:
            if self.api_key_groupbox.isChecked():
                self.provider["apiKey"] = self.api_key_input.text()
        else:
            self.provider = xyz.TileProvider(name=self.provider_input.text(),
                                             url=self.url_input.text(),
                                             attribution=self.provider_input.text(),
                                             min_zoom=self.min_zoom_input.value(),
                                             max_zoom=self.max_zoom_input.value())
        super().accept()

    def sizeHint(self) -> QSize:
        return QSize(768, super().sizeHint().height())

    def keyPressEvent(self, e) -> None:
        # ignore "Enter" key press that would otherwise trigger ok button
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            e.accept()
        else:
            super().keyPressEvent(e)
