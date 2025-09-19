#!/usr/bin/env python3
""" Main module for insarviz time-series visualization tool.

Create the main window and manage links with other sub-windows and loading
data modules.
Contains the following class:
* MainWindow

and function:
* main
"""

from typing import Optional, Any

import logging
import logging.handlers
import multiprocessing

import warnings

import pathlib

import sys

import datetime

import json

import numpy as np

import rasterio.warp

from PySide6.QtWidgets import (
    QSizePolicy, QApplication, QLabel, QWidget,
    QMainWindow, QFileDialog, QToolBar,
    QDockWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QMessageBox, QDialog
)

from PySide6.QtGui import (
    QPixmap, QIcon, QKeySequence, QSurfaceFormat, QOpenGLContext, QOffscreenSurface,
    QUndoStack, QAction,  QActionGroup
)

from PySide6.QtCore import Qt, QCoreApplication, Slot, QDir

import PySide6.QtAsyncio as QtAsyncio

import asyncio
from qasync import QEventLoop, QApplication

import pyqtgraph as pg
import pyqtgraph.exporters
from insarviz.exporters.myCSVExporter import myCSVExporter

from insarviz.Loader import Loader
from insarviz.BandSlider import BandSlider
from insarviz.ColormapWidget import ColormapWidget
from insarviz.map.MapModel import MapModel
from insarviz.map.MapView import MapView
from insarviz.map.MinimapView import MinimapView
from insarviz.plot.PlotModel import PlotModel
from insarviz.plot.TemporalPlotView import TemporalPlotWindow
from insarviz.plot.SpatialPlotView import SpatialPlotWindow
import insarviz.version as version

from insarviz.map.layers.RasterLayerDialog import RasterLayerDialog

from insarviz.custom_widgets import IconDockWidget

from insarviz.utils import openUrl, normalize_path

from insarviz.map.layers.Layer import OpenGLLayer, RasterRGBLayer, Raster1BLayer
from insarviz.map.layers.WMTSLayer import WMTSLayer, WMTSLayerDialog
from insarviz.map.layers.XYZLayer import OpenStreetMapLayer, XYZLayer, XYZLayerDialog
from insarviz.map.layers.SwipeTool import SwipeTool
from insarviz.map.layers.LayerView import LayerView
from insarviz.LoggerWidget import LoggerWidget, LogsStore

logging.getLogger("rasterio").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

log_messages = LogsStore()

queue = multiprocessing.Queue()
queue_handler = logging.handlers.QueueHandler(queue)

queue_listener = logging.handlers.QueueListener(queue,
                                                log_messages,
                                                logging.StreamHandler())
queue_listener.start()

root_logger = logging.getLogger()
root_logger.addHandler(queue_handler)
root_logger.setLevel(logging.INFO)

class MainWindow(QMainWindow):
    """
    The main window of insarviz. Contains every widget and every model.
    """

    def __init__(self, config_dict=None):
        """
        :filepath: the file to load
        :config_dict: the configuration dictionary
        """
        super().__init__()
        # various init:
        self.config_dict = config_dict
        self.project_filepath: Optional[pathlib.Path] = None
        self.setWindowTitle("[*]InsarViz")
        self.setMouseTracking(True)
        self.setDockNestingEnabled(True)
        self.undo_stack: QUndoStack = QUndoStack(self)
        self.undo_stack.cleanChanged.connect(self.on_clean_changed)

        # Loader:
        self.loader: Loader = Loader()

        # Models:
        context: QOpenGLContext = QOpenGLContext()
        context.setShareContext(QOpenGLContext.globalShareContext())
        context.create()
        logger.info(f"Open GL version: {context.format().version()}")
        logger.info(f"Open GL renderable type {context.format().renderableType()}")
        if not context.isValid():
            QMessageBox.critical(self, "Insarviz", "OpenGL error: context is not valid")
            raise RuntimeError("Global OpenGL shared context cannot be created")
        offscreen_surface = QOffscreenSurface()
        offscreen_surface.setFormat(context.format())
        offscreen_surface.create()
        OpenGLLayer.context = context
        OpenGLLayer.offscreen_surface = offscreen_surface
        self.map_model = MapModel(self.loader, context, offscreen_surface)
        self.map_model.opened.connect(self.on_map_model_opened)
        self.map_model.closed.connect(self.on_map_model_closed)
        self.plot_model = PlotModel(self.loader)
        self.map_model.layer_model.selection_initialized.connect(self.plot_model.on_selection_init)
        self.map_model.closed.connect(self.plot_model.close)
        self.map_model.closed.connect(self.undo_stack.clear)
        self.map_model.layer_model.add_undo_command.connect(self.undo_stack.push)

        # Layer manager
        self.layer_model = self.map_model.layer_model
        self.layer_widget = LayerView(self.layer_model)
        # new openstreetmap action
        self.new_openstreetmap_action = QAction(
            QIcon('icons:WMS.svg'), "New OpenStreetMap Layer", self)
        self.new_openstreetmap_action.triggered.connect(self.new_openstreetmap_layer)
        # new WMTS action
        self.new_WMTS_action = QAction(QIcon('icons:WMS.svg'), "New WMTS Layer", self)
        self.new_WMTS_action.triggered.connect(self.new_WMTS_layer)
        # new geomap action
        self.new_XYZ_action = QAction(QIcon('icons:WMS.svg'), "New XYZ Layer", self)
        self.new_XYZ_action.triggered.connect(self.new_XYZ_layer)
        # new raster1B action
        self.new_raster1B_action = QAction(QIcon('icons:raster1B.svg'), "New Raster1B Layer", self)
        self.new_raster1B_action.triggered.connect(self.new_raster1B)
        # new rasterRGB action
        self.new_rasterRGB_action = QAction(QIcon('icons:rasterRGB.svg'),
                                            "New RasterRGB Layer", self)
        self.new_rasterRGB_action.triggered.connect(self.new_rasterRGB)
        # new swipe action
        self.new_swipe_action = QAction(QIcon("icons:swipetool.png"), "New Swipe Tool", self)
        self.new_swipe_action.triggered.connect(self.new_swipe_layer)
        # show all action
        self.layer_showall_action = QAction(QIcon('icons:eye_open.svg'), "Show all", self)
        self.layer_showall_action.setToolTip("Show all layers")
        self.layer_showall_action.triggered.connect(self.layer_model.show_all_layers)
        # hide all action
        self.layer_hideall_action = QAction(QIcon('icons:eye_closed.svg'), "Hide all", self)
        self.layer_hideall_action.setToolTip("Hide all layers")
        self.layer_hideall_action.triggered.connect(self.layer_model.hide_all_layers)
        # move up action
        self.layer_moveup_action = QAction(QIcon('icons:arrowup.png'), "Move Up", self)
        self.layer_moveup_action.setToolTip("Move up layer")
        self.layer_moveup_action.triggered.connect(lambda: self.layer_model.move_layer_up(
            self.layer_widget.proxy_model.mapToSource(
                self.layer_widget.selectionModel().currentIndex())))
        self.layer_model.current_movable_up.connect(self.layer_moveup_action.setEnabled)
        # move down action
        self.layer_movedown_action = QAction(QIcon('icons:arrowdown.png'), "Move Down", self)
        self.layer_movedown_action.setToolTip("Move down layer")
        self.layer_movedown_action.triggered.connect(lambda: self.layer_model.move_layer_down(
            self.layer_widget.proxy_model.mapToSource(
                self.layer_widget.selectionModel().currentIndex())))
        self.layer_model.current_movable_down.connect(self.layer_movedown_action.setEnabled)
        # remove action
        self.layer_remove_action = QAction(QIcon('icons:remove.png'), "Remove", self)
        self.layer_remove_action.setToolTip("Remove item")
        self.layer_remove_action.setShortcuts(QKeySequence.StandardKey.Delete)
        self.layer_remove_action.triggered.connect(lambda: self.layer_model.remove(
            self.layer_widget.proxy_model.mapToSource(
                self.layer_widget.selectionModel().currentIndex())))
        self.layer_model.current_removable.connect(self.layer_remove_action.setEnabled)
        # action group
        self.layer_action_group = QActionGroup(self)
        self.layer_action_group.addAction(self.layer_moveup_action)
        self.layer_action_group.addAction(self.layer_movedown_action)
        self.layer_action_group.addAction(self.layer_showall_action)
        self.layer_action_group.addAction(self.layer_hideall_action)
        self.layer_action_group.addAction(self.layer_remove_action)
        self.layer_action_group.addAction(self.new_openstreetmap_action)
        self.layer_action_group.addAction(self.new_WMTS_action)
        self.layer_action_group.addAction(self.new_XYZ_action)
        self.layer_action_group.addAction(self.new_swipe_action)
        self.layer_action_group.addAction(self.new_raster1B_action)
        self.layer_action_group.addAction(self.new_rasterRGB_action)
        self.layer_action_group.setExclusive(False)
        self.layer_action_group.setDisabled(True)
        self.geolocated_action_group = QActionGroup(self)
        self.geolocated_action_group.addAction(self.new_openstreetmap_action)
        self.geolocated_action_group.addAction(self.new_WMTS_action)
        self.geolocated_action_group.addAction(self.new_XYZ_action)
        self.geolocated_action_group.setExclusive(False)
        self.geolocated_action_group.setDisabled(True)
        # layout
        layer_layout = QVBoxLayout()
        layer_toolbar = QToolBar(self)
        layer_toolbar.addAction(self.layer_moveup_action)
        layer_toolbar.addAction(self.layer_movedown_action)
        layer_toolbar.addAction(self.layer_showall_action)
        layer_toolbar.addAction(self.layer_hideall_action)
        layer_toolbar.addAction(self.layer_remove_action)
        layer_layout.addWidget(layer_toolbar)
        layer_layout.addWidget(self.layer_widget)
        layer_manager_widget = QWidget()
        layer_manager_widget.setLayout(layer_layout)
        self.layer_dockwidget = QDockWidget('Layers', self)
        self.layer_dockwidget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.layer_dockwidget.setWidget(layer_manager_widget)

        # Map:
        self.map_widget = MapView(self.map_model, self)
        self.map_widget.setMouseTracking(True)
        self.map_widget.pointer_changed.connect(self.plot_model.update_pointer)
        self.map_widget.interaction_changed.connect(self.on_mapview_interaction_changed)
        self.plot_model.updated_pointer_info.connect(self.map_widget.update_mouse_tooltip)

        # Minimap
        self.minimap_widget = MinimapView(self.map_model, self)
        self.minimap_widget.pan_map_view.connect(self.map_widget.pan)
        self.minimap_widget.zoom_map_view.connect(self.map_widget.zoom)
        self.minimap_widget.set_center_map_view.connect(self.map_widget.set_view_center)
        self.map_widget.viewport_matrix_changed.connect(
            self.minimap_widget.update_mapview_viewport_matrix)
        self.minimap_dock_widget = QDockWidget('Minimap', self)
        self.minimap_dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.minimap_dock_widget.setWidget(self.minimap_widget)

        # Colormap
        self.colormap_widget = ColormapWidget(self)
        # connect signals to slots
        self.map_model.closed.connect(self.colormap_widget.on_close)
        self.map_model.total_hist_changed.connect(self.colormap_widget.set_total_histogram)
        self.map_model.band_hist_changed.connect(self.colormap_widget.set_band_histogram)
        self.map_model.request_colormap.connect(self.colormap_widget.set_colormap)
        self.map_model.v0_v1_changed.connect(self.colormap_widget.set_v0_v1)
        self.loader.data_units_loaded.connect(self.colormap_widget.set_data_units)
        self.loader.histograms_computed.connect(self.colormap_widget.on_histograms_computed)
        self.loader.computing_histograms.connect(self.colormap_widget.on_compute_histogram)
        self.colormap_widget.colormap_changed.connect(self.map_model.set_colormap)
        self.colormap_widget.v0_v1_changed.connect(self.map_model.set_v0_v1)
        self.colormap_widget.compute_histograms.connect(self.loader.compute_histograms)
        self.colormap_widget.cancel_compute_histograms.connect(
            self.loader.cancel_compute_histograms)

        # dates slider:
        self.band_slider = BandSlider(self.loader)
        self.band_slider.value_changed.connect(self.map_model.show_band)
        self.map_model.closed.connect(self.band_slider.on_close)
        self.loader.data_loaded.connect(self.band_slider.on_data_loaded)

        # plot windows:
        # temporal window
        self.temporal_plot_window = TemporalPlotWindow(self.plot_model)
        self.band_slider.value_changed.connect(
            self.temporal_plot_window.plot_widget.date_marker.on_slider_changed)
        self.temporal_plot_window.plot_widget.date_marker.pos_changed.connect(
            self.band_slider.set_value)
        self.map_widget.request_lock_axes.connect(lambda: self.temporal_plot_window.checkbox_axes.setCheckState(Qt.CheckState.Checked))

        self.temporal_plot_dock = IconDockWidget(
            "Temporal profile", self, QIcon('icons:temporal.svg'))
        self.temporal_plot_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.temporal_plot_dock.setWidget(self.temporal_plot_window)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.temporal_plot_dock)
        # spatial window
        self.spatial_plot_window = SpatialPlotWindow(self.plot_model)
        self.spatial_plot_dock = IconDockWidget(
            "Spatial profile", self, QIcon('icons:spatial.svg'))
        self.spatial_plot_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.spatial_plot_dock.setWidget(self.spatial_plot_window)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.spatial_plot_dock)
        # layout
        self.tabifyDockWidget(self.temporal_plot_dock, self.spatial_plot_dock)
        self.temporal_plot_dock.hide()
        self.spatial_plot_dock.hide()

        # Main layout:
        self.main_widget = QSplitter(Qt.Orientation.Horizontal)
        self.main_widget.setChildrenCollapsible(False)
        self.map_band_slider_layout = QVBoxLayout()
        self.map_band_slider_layout.addWidget(self.band_slider)
        self.map_band_slider_layout.addWidget(self.map_widget, stretch=1)
        self.map_band_slider_widget = QWidget()
        self.map_band_slider_widget.setLayout(self.map_band_slider_layout)
        self.main_widget.addWidget(self.map_band_slider_widget)
        self.main_widget.addWidget(self.colormap_widget)
        self.main_widget.setCollapsible(self.main_widget.indexOf(self.colormap_widget), True)
        self.setCentralWidget(self.main_widget)
        self.main_widget.resize(250, 250)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.layer_dockwidget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.minimap_dock_widget)

        # Status bar / footer
        # Logo & version
        self.logo_widget = QLabel(self)
        pix = QPixmap('icons:logo_insarviz.png')
        self.logo_widget.setPixmap(
            pix.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation))
        logo_text_widget = QLabel(f"InsarViz v.{version.__version__}", self)
        # logo_text_widget.setFont(QFont("Arial", 15, QFont.Bold))
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_widget)
        logo_layout.addWidget(logo_text_widget)
        logoandtext_widget = QWidget()
        logoandtext_widget.setLayout(logo_layout)
        self.statusBar().addPermanentWidget(logoandtext_widget)
        # Point info
        self.info_widget = QLabel('x=  , y=  ,z=  ')
        self.info_widget.setMargin(3)
        self.plot_model.updated_pointer_info.connect(self.update_cursor_info)
        self.statusBar().addWidget(self.info_widget)

        log_messages.new_record.connect(self._on_new_log_message)

        # selection toolbar
        self.plotting_toolbar = QToolBar("Selection toolbar")
        self.plotting_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.inter_action = QAction("Interactive", self)
        self.inter_action.setToolTip("Interactive (Alt+1)")
        self.inter_action.setIcon(QIcon('icons:cursor.png'))
        self.inter_action.triggered.connect(lambda x:
                                            self.map_widget.set_interaction(MapView.INTERACTIVE)
                                            if x else None)
        self.inter_action.setCheckable(True)
        self.inter_action.trigger()
        self.inter_action.setShortcut('Alt+1')

        self.points_action = QAction("Point", self)
        self.points_action.setToolTip("Point (Alt+2)")
        self.points_action.setIcon(QIcon('icons:points.png'))
        self.points_action.setIconText("Point")
        self.points_action.setCheckable(True)
        self.points_action.toggled.connect(lambda x: self.map_widget.set_interaction(MapView.POINTS)
                                           if x else None)
        self.points_action.setShortcut('Alt+2')

        self.prof_action = QAction("Profile", self)
        self.prof_action.setToolTip("Profile (Alt+3)")
        self.prof_action.setIcon(QIcon('icons:profile.png'))
        self.prof_action.setIconText("Profile")
        self.prof_action.setCheckable(True)
        self.prof_action.toggled.connect(lambda x: self.map_widget.set_interaction(MapView.PROFILE)
                                         if x else None)
        self.prof_action.setShortcut('Alt+3')

        self.ref_action = QAction("Reference", self)
        self.ref_action.setToolTip("Reference (Alt+4)")
        self.ref_action.setIcon(QIcon('icons:ref.png'))
        self.ref_action.setIconText("Reference")
        self.ref_action.setCheckable(True)
        self.ref_action.toggled.connect(lambda x: self.map_widget.set_interaction(MapView.REF)
                                        if x else None)
        self.ref_action.setShortcut('Alt+4')

        # action group so that only one tool can be selected at the same time
        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)
        self.action_group.addAction(self.inter_action)
        self.action_group.addAction(self.points_action)
        self.action_group.addAction(self.prof_action)
        self.action_group.addAction(self.ref_action)
        self.action_group.setDisabled(True)
        # spacers to center buttons:
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plotting_toolbar.addWidget(spacer)
        self.plotting_toolbar.addAction(self.inter_action)
        self.plotting_toolbar.addAction(self.points_action)
        self.plotting_toolbar.addAction(self.prof_action)
        self.plotting_toolbar.addAction(self.ref_action)
        self.plotting_toolbar.addWidget(spacer2)
        self.addToolBar(self.plotting_toolbar)

        # Menu
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        # File Menu
        file_menu = menubar.addMenu('File')
        open_action = QAction("Open data cube or project", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open)

        self.save_action = QAction("Save", self)
        self.save_action.triggered.connect(self.save)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setDisabled(True)
        self.save_as_project_action = QAction("Save as project", self)
        self.save_as_project_action.triggered.connect(self.save_as_project)
        self.save_as_project_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_project_action.setDisabled(True)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)

        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_project_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        # Edit Menu
        edit_menu = menubar.addMenu('Edit')
        undo_action = self.undo_stack.createUndoAction(self, "Undo")
        undo_action.setIcon(QIcon("icons:undo.svg"))
        undo_action.setShortcuts(QKeySequence.StandardKey.Undo)

        redo_action = self.undo_stack.createRedoAction(self, "Redo")
        redo_action.setIcon(QIcon("icons:redo.svg"))
        redo_action.setShortcuts(QKeySequence.StandardKey.Redo)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # Layer Menu
        layer_menu = menubar.addMenu('Layer')
        layer_menu.addAction(self.layer_moveup_action)
        layer_menu.addAction(self.layer_movedown_action)
        layer_menu.addAction(self.layer_showall_action)
        layer_menu.addAction(self.layer_hideall_action)
        layer_menu.addAction(self.layer_remove_action)
        layer_menu.addSeparator()
        layer_menu.addAction(self.new_swipe_action)
        layer_menu.addSeparator()
        layer_menu.addAction(self.new_openstreetmap_action)
        layer_menu.addAction(self.new_WMTS_action)
        layer_menu.addAction(self.new_XYZ_action)
        layer_menu.addAction(self.new_raster1B_action)
        layer_menu.addAction(self.new_rasterRGB_action)

        # View Menu
        view_menu = menubar.addMenu('View')
        self.plot_act = QAction("Plotting", self)
        self.plot_act.setCheckable(True)
        self.plot_act.setChecked(False)
        self.plot_act.setEnabled(False)
        self.plot_act.toggled.connect(self.show_plot_window)
        self.plot_act.setShortcut('Ctrl+P')
        view_menu.addAction(self.plot_act)

        self.minimap_action = QAction("Minimap", self)
        self.minimap_action.setCheckable(True)
        self.minimap_action.setChecked(True)
        self.minimap_action.toggled.connect(self.minimap_dock_widget.setVisible)
        self.minimap_dock_widget.visibilityChanged.connect(self.minimap_action.setChecked)
        view_menu.addAction(self.minimap_action)

        self.flip_h_action = QAction("Flip Horizontally", self)
        self.flip_h_action.setToolTip("Flip map horizontally")
        self.flip_h_action.setCheckable(True)
        self.flip_h_action.setChecked(False)
        self.flip_h_action.toggled.connect(self.map_model.set_flip_h)
        self.flip_v_action = QAction("Flip Vertically", self)
        self.flip_v_action.setToolTip("Flip map vertically")
        self.flip_v_action.setCheckable(True)
        self.flip_v_action.setChecked(False)
        self.flip_v_action.toggled.connect(self.map_model.set_flip_v)
        self.flip_group = QActionGroup(self)
        self.flip_group.addAction(self.flip_h_action)
        self.flip_group.addAction(self.flip_v_action)
        self.flip_group.setExclusive(False)
        self.flip_group.setDisabled(True)
        view_menu.addSeparator()
        view_menu.addAction(self.flip_h_action)
        view_menu.addAction(self.flip_v_action)

        # Help Menu
        help_menu = menubar.addMenu('Help')
        help_action = QAction("Documentation", self)
        help_action.triggered.connect(openUrl)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_menu.addAction(help_action)
        show_log_action = QAction("Show InsarViz logs", self)
        show_log_action.triggered.connect(self.show_log_messages_dialog)
        help_menu.addAction(show_log_action)

    @Slot()
    def show_log_messages_dialog(self):
        dialog = QDialog(self)
        dialog.resize(600, 400)
        logger_widget = LoggerWidget(log_messages)
        layout = QVBoxLayout(dialog)
        layout.addWidget(logger_widget)
        dialog.setModal(True)
        dialog.setWindowTitle("InsarViz logs")
        dialog.setLayout(layout)
        dialog.show()

    @Slot()
    def _on_new_log_message(self):
        last_record = log_messages.records[-1]
        if last_record.levelno >= logging.ERROR:
            QMessageBox.critical(self, "Insarviz - Critical error", last_record.msg)

    def load_data(self, filepath_string: str) -> bool:
        # if unsaved changes propose to save
        if not self.undo_stack.isClean():
            changes_managed = False
            while not changes_managed:
                user_input = QMessageBox.warning(self, "Changes not saved",
                                                 "Unsaved changes.\nDo you want to save them inside a project ?",
                                                 QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                                 QMessageBox.StandardButton.Save)
                if user_input == QMessageBox.StandardButton.Save:
                    if self.save_as_project():
                        changes_managed = True
                elif user_input == QMessageBox.StandardButton.Discard:
                    changes_managed = True
                elif user_input == QMessageBox.StandardButton.Cancel:
                    return False
        # close current project
        self.map_model.close()
        # open new project or cube
        filepath = normalize_path(filepath_string)
        logger.info(f"loading {filepath}")
        extension = filepath.suffix
        if extension == ".json":
            #  opening insarviz project
            input_dict: dict[str, Any]
            with open(filepath, "r", encoding="utf-8") as file:
                try:
                    input_dict = json.load(file)
                except json.JSONDecodeError:
                    logger.warning(f"JSON decoder error on {filepath}")
                    QMessageBox.critical(self, "File Open Error",
                                         f"{filepath}\nJSON decoder error (not a correct JSON file).")
                    return False
            try:
                logger.info(f"{filepath} is an insarviz project version {input_dict['insarviz']}")
            except KeyError:
                logger.warning(f"{filepath} is not an insarviz project")
                QMessageBox.critical(self, "File Open Error",
                                     f"{filepath}\nis not an insarviz project.")
                return False
            try:
                self.loader.open(normalize_path(input_dict["dataset_path"], filepath.as_posix()))
            except rasterio.errors.RasterioIOError as e:
                logger.warning(repr(e))
                QMessageBox.critical(self, "File Open Error", repr(e))
                return False
            try:
                if not self.map_model.from_dict(input_dict, filepath, self.map_widget):
                    logger.warning(
                        f"{filepath} is an insarviz project but its structure is not correct")
                    self.undo_stack.clear()
                    QMessageBox.critical(self, "File Open Error",
                                         f"{filepath}\nis an insarviz project but its structure is not correct")
                    return False
            except rasterio.errors.RasterioIOError as e:
                logger.warning(repr(e))
                self.map_model.close()
                QMessageBox.critical(self, "File Open Error", repr(e))
                return False
            self.project_filepath = filepath
        else:
            # opening cube directly (without project)
            try:
                self.loader.open(filepath)
            except rasterio.errors.RasterioIOError:
                logger.warning(f"gdal cannot open {filepath}")
                QMessageBox.critical(self, "File Open Error",
                                     f"Rasterio / GDAL cannot open:\n{filepath}")
                return False
            self.map_model.create_base_layers()
        logger.info(f"{filepath} successfully loaded")
        # enable plot button in menu:
        self.plot_act.setEnabled(True)
        self.undo_stack.clear()
        self.map_model.opened.emit()
        if self.loader.dataset.crs is None:
            self.geolocated_action_group.setDisabled(True)
        else:
            self.geolocated_action_group.setEnabled(True)
        self.band_slider.set_value(self.map_model.current_band_index)
        self.band_slider.set_reference_band_index(self.loader.reference_band_index)
        self.band_slider.setEnabled(True)
        self.setWindowTitle(f"{str(filepath)}[*] - Insarviz")
        return True

    @Slot(int)
    def on_mapview_interaction_changed(self, value: int) -> None:
        if value == MapView.INTERACTIVE:
            self.inter_action.setChecked(True)
        elif value == MapView.POINTS:
            self.points_action.setChecked(True)
        elif value == MapView.PROFILE:
            self.prof_action.setChecked(True)
        elif value == MapView.REF:
            self.ref_action.setChecked(True)

    @Slot(tuple, np.ndarray)
    def update_cursor_info(self, info: tuple, _: np.ndarray) -> None:
        """
        update point information (x, y, value) in Informations widget as
        cursor hovers over Map

        Parameters
        ----------
        info : tuple (x, y, date, value)
            values of the point currently hovered over in MapView.
        """
        if info == ():
            self.info_widget.setText("")
        else:
            assert self.loader.dataset is not None
            x, y, date, value = info
            if isinstance(date, int):
                date = f"band #{date}"
            elif isinstance(date, datetime.datetime):
                date = date.date()
            text = f"x:{x:5d}, y:{y:5d}, val:{value:7.3f}, date:{date}"
            if self.loader.dataset.crs is not None:
                x_coord, y_coord = self.loader.dataset.xy(y, x)
                long, lat = rasterio.warp.transform(self.loader.dataset.crs,
                                                    rasterio.crs.CRS.from_epsg(4326),
                                                    [x_coord], [y_coord])
                text = text + f", lat:{lat[0]:7.3f}, long:{long[0]:7.3f}"
            self.info_widget.setText(text)

    def show_plot_window(self, checked: bool) -> None:
        if checked:
            self.temporal_plot_dock.show()
            self.spatial_plot_dock.show()
        else:
            self.temporal_plot_dock.hide()
            self.spatial_plot_dock.hide()

    def closeEvent(self, event) -> None:
        if not self.undo_stack.isClean():
            changes_managed = False
            while not changes_managed:
                user_input = QMessageBox.warning(self, "Changes not saved",
                                                 "Unsaved changes.\nDo you want to save them inside a project ?",
                                                 QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                                 QMessageBox.StandardButton.Save)
                if user_input == QMessageBox.StandardButton.Save:
                    if self.save_as_project():
                        changes_managed = True
                elif user_input == QMessageBox.StandardButton.Discard:
                    changes_managed = True
                elif user_input == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
        self.map_model.close()
        print('\n *** Thank you for using InsarViz, see you soon! *** \n')
        super().closeEvent(event)

    def new_rasterRGB(self) -> None:
        # the second return value of QFileDialog.getOpenFileName is the filter selected by user
        filepath_string, _ = QFileDialog.getOpenFileName(self, "Select file")
        filepath = normalize_path(filepath_string)
        if filepath:
            with warnings.catch_warnings():
                # ignore RuntimeWarning for slices that contain only nans
                warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning,
                                        message="Dataset has no geotransform, gcps, or rpcs. The identity matrix will be returned.")
                try:
                    with rasterio.open(filepath) as file:
                        assert ((file.crs is not None and self.loader.dataset.crs is not None) or
                                (file.shape == self.loader.dataset.shape))
                        input_bands = [(f"{file.indexes[i]}: {file.descriptions[i]}"
                                        if file.descriptions[i] is not None else
                                        f"{file.indexes[i]}") for i in range(file.count)]
                        dialog = RasterLayerDialog(input_bands, RasterRGBLayer.nb_band,
                                                   ["R", "G", "B"], parent=self)
                        dialog.exec()
                        if dialog.result() == QDialog.DialogCode.Accepted:
                            R = file.indexes[dialog.band_comboboxes[0].currentIndex()]
                            G = file.indexes[dialog.band_comboboxes[1].currentIndex()]
                            B = file.indexes[dialog.band_comboboxes[2].currentIndex()]
                            mask = (file.indexes[dialog.mask_combobox.currentIndex()]
                                    if dialog.mask_checkbox.isChecked() else None)
                            self.map_model.layer_model.add_layer(
                                RasterRGBLayer(filepath.name, self.map_model, filepath,
                                               R, G, B, mask))
                except rasterio.errors.RasterioIOError:
                    QMessageBox.critical(self, "File Open Error",
                                         f"Cannot open\n{filepath}\nwith rasterio.")
                except AssertionError:
                    QMessageBox.critical(
                        self, "File Open Error", f"{filepath}\nDoes not have the same size as the dataset and is not geolocalized.")

    def new_raster1B(self) -> None:
        # the second return value of QFileDialog.getOpenFileName is the filter selected by user
        filepath_string, _ = QFileDialog.getOpenFileName(self, "Select file")
        filepath = normalize_path(filepath_string)
        if filepath:
            with warnings.catch_warnings():
                # ignore RuntimeWarning for slices that contain only nans
                warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning,
                                        message="Dataset has no geotransform, gcps, or rpcs. The identity matrix will be returned.")
                try:
                    with rasterio.open(filepath) as file:
                        assert ((file.crs is not None and self.loader.dataset.crs is not None) or
                                (file.shape == self.loader.dataset.shape))
                        if file.count == 1:
                            self.map_model.layer_model.add_layer(
                                Raster1BLayer(filepath.name, self.map_model, filepath, 1, mask=None))
                        else:
                            input_bands = [(f"{file.indexes[i]}: {file.descriptions[i]}"
                                            if file.descriptions[i] is not None else
                                            f"{file.indexes[i]}") for i in range(file.count)]
                            dialog = RasterLayerDialog(input_bands, Raster1BLayer.nb_band,
                                                       ["Band"], parent=self)
                            dialog.exec()
                            if dialog.result() == QDialog.DialogCode.Accepted:
                                b = file.indexes[dialog.band_comboboxes[0].currentIndex()]
                                mask = (file.indexes[dialog.mask_combobox.currentIndex()]
                                        if dialog.mask_checkbox.isChecked() else None)
                                self.map_model.layer_model.add_layer(
                                    Raster1BLayer(filepath.name, self.map_model, filepath, b, mask))
                except rasterio.errors.RasterioIOError:
                    QMessageBox.critical(self, "File Open Error",
                                         f"Cannot open\n{filepath}\nwith rasterio.")
                except AssertionError:
                    QMessageBox.critical(
                        self, "File Open Error", f"{filepath}\nDoes not have the same size as the dataset and is not geolocalized.")

    def new_openstreetmap_layer(self) -> None:
        new_layer = OpenStreetMapLayer(self.map_model, self.map_widget)
        self.map_model.layer_model.add_layer(new_layer)

    def new_WMTS_layer(self) -> None:
        dialog = WMTSLayerDialog(parent=self)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Accepted:
            server = dialog.server_input.text()
            layer = dialog.layer_input.text()
            tilematrixset = dialog.tilematrixset_input.text()
            try:
                new_layer = WMTSLayer(layer, self.map_model, self.map_widget,
                                      server, layer, tilematrixset)
            except (RuntimeError, KeyError) as e:
                logger.warning(repr(e))
                return
            self.map_model.layer_model.add_layer(new_layer)

    def new_XYZ_layer(self) -> None:
        dialog = XYZLayerDialog(parent=self)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Accepted:
            provider = dialog.provider
            try:
                new_layer = XYZLayer(provider.name, self.map_model, self.map_widget, provider)
            except (RuntimeError, KeyError) as e:
                logger.warning(repr(e))
                return
            self.map_model.layer_model.add_layer(new_layer)

    def new_swipe_layer(self) -> None:
        self.map_model.layer_model.add_layer(SwipeTool(dataset = self.loader.dataset))

    def open(self) -> None:
        # the second return value of QFileDialog.getOpenFileName is the filter selected by user
        filepath, _ = QFileDialog.getOpenFileName(self, "Select file")
        if filepath:
            self.load_data(filepath)

    def save_as_project(self) -> bool:
        filter_string = "Insarviz project (*.json)"
        # the second return value of QFileDialog.getOpenFileName is the filter selected by user
        filepath_string, _ = QFileDialog.getSaveFileName(self, "Save insarviz project to ...",
                                                         filter=filter_string)
        if filepath_string:
            filepath = pathlib.Path(filepath_string)
            extension = filepath.suffix
            if extension == "":
                filepath = filepath.with_suffix(".json")
            self.project_filepath = filepath
            return self.save()
        return False

    def save(self) -> bool:
        if self.project_filepath is not None:
            try:
                extension = self.project_filepath.suffix
                if extension != ".json":
                    raise ValueError
                with open(self.project_filepath, "w", encoding="utf-8") as file:
                    json.dump(self.map_model.to_dict(self.project_filepath), file, indent=4)
                self.undo_stack.setClean()
                logger.info(f"Project saved at {self.project_filepath}")
                self.setWindowTitle(f"{str(self.project_filepath)}[*] - Insarviz")
                return True
            except ValueError:
                error_message = f"Cannot save project at:\n{self.project_filepath}\nWrong file extension (should be .json)."
                logger.warning(error_message)
                QMessageBox.critical(self, "Save Error", error_message)
                return False
            except FileNotFoundError:
                error_message = f"Cannot save project at:\n{self.project_filepath}\nFileNotFoundError."
                logger.critical(error_message)
                QMessageBox.critical(self, "Save Error", error_message)
                return False
        return False

    def on_clean_changed(self, v: bool) -> None:
        self.setWindowModified(not v)
        if not v and self.project_filepath:
            self.save_action.setEnabled(True)
        else:
            self.save_action.setDisabled(True)

    def on_map_model_opened(self) -> None:
        self.layer_action_group.setEnabled(True)
        self.action_group.setEnabled(True)
        self.flip_group.setEnabled(True)
        self.save_as_project_action.setEnabled(True)

    def on_map_model_closed(self) -> None:
        self.project_filepath = None
        self.layer_action_group.setDisabled(True)
        self.geolocated_action_group.setDisabled(True)
        self.action_group.setDisabled(True)
        self.flip_group.setDisabled(True)
        self.save_action.setDisabled(True)
        self.save_as_project_action.setDisabled(True)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="insar timeseries visualisation")
    parser.add_argument("-v", type=int, default=3,
                        help=("set logging level:"
                              "0 critical, 1 error, 2 warning,"
                              "3 info, 4 debug, default=info"))
    parser.add_argument("-i", type=str, default=None, help="input filepath")
    parser.add_argument("-p", type=str, default=None,
                        help="directory that contains user defined plugins")
    args = parser.parse_args()
    logging_translate = [logging.CRITICAL,
                         logging.ERROR,
                         logging.WARNING,
                         logging.INFO,
                         logging.DEBUG]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging_translate[args.v])
    config = None
    if args.p:
        config = {"plugin_directory": args.p}
        logger.info(f"adding {args.p} as plugin_directory")
    # OpenGL widgets share context even belonging in different windows
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    # set OpenGL profile
    opengl_format: QSurfaceFormat = QSurfaceFormat.defaultFormat()
    opengl_format.setVersion(4, 1)
    opengl_format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    opengl_format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    opengl_format.setOption(QSurfaceFormat.FormatOption.DeprecatedFunctions, False)
    QSurfaceFormat.setDefaultFormat(opengl_format)
    # set pyqtgraph options
    pg.setConfigOption("background", 'w')
    pg.setConfigOption("foreground", 'k')
    # replace csv exporter by custom csv exporter:
    pg.exporters.Exporter.Exporters.pop(
        pg.exporters.Exporter.Exporters.index(
            pyqtgraph.exporters.CSVExporter))
    pg.exporters.Exporter.Exporters.insert(0, myCSVExporter)
    # add icons directory to Qt paths
    script_dir: pathlib.Path = pathlib.Path(__file__).parent  # directory of ts_viz.py
    icons_dir: pathlib.Path = script_dir / "icons"
    QDir.addSearchPath('icons', str(icons_dir))
    # create application
    app: QApplication = QApplication([])
    main_window = MainWindow(config_dict=config)
    main_window.show()
    # focus on mainwindow
    main_window.showMaximized()
    main_window.activateWindow()
    # main_window2 = MainWindow(filepath=args.i, config_dict=config)
    # main_window2.show()

    # QTASYNCIO
    # QtAsyncio.run(handle_sigint=True)
    # sys.exit(app.exec())
    # END QTASYNCIO

    # QASYNC
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    async def async_main():
        # loading directly if file specified upon app launch:
        if args.i is not None:
            main_window.load_data(args.i)
        await app_close_event.wait()

    with event_loop:
        event_loop.run_until_complete(async_main())
    # END QASYNC
    app.quit()
    queue_listener.stop()
    sys.exit(0)

if __name__ == '__main__':
    main()
