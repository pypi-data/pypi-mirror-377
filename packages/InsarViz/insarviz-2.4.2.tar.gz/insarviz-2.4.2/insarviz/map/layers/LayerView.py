# -*- coding: utf-8 -*-
"""
LayerView

This module contains the LayerView and LayerWidget classes managing the layer manager widget.
"""

# imports ##########################################################################################

from typing import Optional
import rasterio

from PySide6.QtCore import (
    Qt, QObject, Signal, Slot, QModelIndex, QSize, QItemSelectionModel,
    QSortFilterProxyModel, QAbstractItemModel, QEvent
)

from PySide6.QtGui import QIcon, QPalette, QPainter, QImage, QPen, QBrush, QColor

from PySide6.QtWidgets import (
    QSlider,
    QTreeView, QAbstractItemView, QStyledItemDelegate,
    QHeaderView, QApplication, QStyle, QStyleOptionButton, QStyleOptionViewItem,
    QSpinBox, QDoubleSpinBox, QColorDialog, QPushButton, QWidget, QDialog, QLabel,
    QVBoxLayout, QLayout, QSizePolicy, QWidget
)

from pyqtgraph.colormap import ColorMap

from insarviz.map.layers.LayerModel import LayerModel, SetDataCommand

from insarviz.map.layers.RasterLayerColorMapEditor import RasterLayerColorMapEditor

from insarviz.Roles import Roles

class SliderWithValue(QWidget):
    SLIDER_SENSITIVITY: float = 1000.0

    sliderMoved = Signal(float)
    sliderReleased = Signal()

    def __init__(self, parent = None, display_value = str, *args):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.display_value = display_value
        self.initial_value = None

        self.slider = QSlider()
        self.slider.setFocusProxy(self)

        label = QLabel("0")
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        def set_label_value(v):
            label.setText(self.display_value(v / self.SLIDER_SENSITIVITY))
        self.slider.valueChanged.connect(set_label_value)
        def on_slider_moved(v):
            self.sliderMoved.emit(v / self.SLIDER_SENSITIVITY)
        self.slider.sliderMoved.connect(on_slider_moved)
        self.slider.sliderMoved.connect(set_label_value)
        self.slider.sliderReleased.connect(lambda: self.sliderReleased.emit())
        def on_slider_pressed():
            self.initial_value = self.value()
        self.slider.sliderPressed.connect(on_slider_pressed)

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        layout.addWidget(self.slider)
        layout.addWidget(label)

    def setMinimum(self, vmin):
        self.slider.setMinimum(int(vmin * self.SLIDER_SENSITIVITY))
    def setMaximum(self, vmax):
        self.slider.setMaximum(int(vmax * self.SLIDER_SENSITIVITY))
    def setValue(self, value):
        self.slider.setValue(int(value * self.SLIDER_SENSITIVITY))
    def value(self):
        return self.slider.value() / self.SLIDER_SENSITIVITY

    def setDisplayValue(self, display_value):
        self.display_value = display_value


# LayerView class ##################################################################################
class LayerView(QTreeView):

    # TODO display branches ? https://doc.qt.io/qt-6/stylesheet-examples.html#customizing-qtreeview

    def __init__(self, layer_model: LayerModel):
        super().__init__()
        self.layer_model = layer_model
        # use proxy model to remove empty SelectionFolders
        self.proxy_model = ProxyLayerModel()
        self.proxy_model.setSourceModel(self.layer_model)
        self.setModel(self.proxy_model)
        # formatting of the view
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        palette: QPalette = QPalette(self.palette())
        palette.setColor(QPalette.ColorRole.Highlight, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)
        # Not all rows have the same height (slider layers)
        # self.setUniformRowHeights(True)
        self.setItemDelegateForColumn(0, ItemDelegate(self))
        self.remove_delegate = RemoveDelegate(self)
        self.setItemDelegateForColumn(1, self.remove_delegate)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.showDropIndicator()
        self.setMouseTracking(True)  # needed for self.entered signal
        # signals and slots connection
        self.entered.connect(self.create_remove_editor)
        self.remove_delegate.clicked.connect(self.remove)
        self.selectionModel().currentChanged.connect(
            lambda x, _: self.layer_model.manage_current_changed(self.proxy_model.mapToSource(x)))
        self.layer_model.rowsMoved.connect(self.update_current_from_move)
        self.layer_model.request_expand.connect(
            lambda i: self.expand(self.proxy_model.mapFromSource(i)))

    # connectd to LayerView.entered
    @Slot(QModelIndex)
    def create_remove_editor(self, index: QModelIndex) -> bool:
        if not index.isValid():
            return False
        if index.column() == self.layer_model.remove_column and \
                self.selectionModel().isRowSelected(index.row(), index.parent()):
            self.edit(index)
            return True
        return False

    # connected to RemoveDelegate.clicked
    @Slot(QModelIndex)
    def remove(self, index: QModelIndex) -> None:
        if index.isValid():
            target: QModelIndex = self.proxy_model.mapToSource(index.siblingAtColumn(0))
            self.layer_model.remove(target)

    # connected to LayerModel.rowsMoved
    @Slot(QModelIndex, int, int, QModelIndex, int)
    def update_current_from_move(self, parent: QModelIndex, start: int, end: int, dest: QModelIndex,
                                 row: int) -> None:
        """
        Update self.currentIndex when layers are moved (drag and drop or up/down button)
        """
        parent = self.proxy_model.mapFromSource(parent)
        dest = self.proxy_model.mapFromSource(dest)
        if parent == QModelIndex() and parent == dest and start == end:
            flags = (QItemSelectionModel.SelectionFlag.SelectCurrent |
                     QItemSelectionModel.SelectionFlag.Rows)
            if start < row:
                row -= 1
            index: QModelIndex = self.proxy_model.index(row, 0, parent)
            self.selectionModel().clear()
            self.selectionModel().setCurrentIndex(index, flags)


# ProxyLayerModel class ############################################################################

class ProxyLayerModel(QSortFilterProxyModel):
    """
    Proxy filter model that filters out empty selection folders. As recursive filtering is enabled,
    the filter is applied on parents (i.e. selection folders) when their children (i.e. selection
    items) are added/modified/removed.
    """

    def __init__(self):
        super().__init__()
        self.setRecursiveFilteringEnabled(True)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # pylint: disable=missing-function-docstring, invalid-name
        index: QModelIndex = self.sourceModel().index(source_row, 0, source_parent)
        if self.sourceModel().data(index, Roles.FolderRole) == "SELECTION_FOLDER":
            if self.sourceModel().rowCount(index) == 0:
                # if empty SelectionFolder then filter out
                return False
        return True


# ItemDelegate class ###############################################################################

class ItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        editor_role: Optional[str] = index.data(Roles.EditorRole)
        editor: QWidget
        if editor_role == "integer":
            editor = QSpinBox(parent)
            editor.setFrame(False)
            return editor
        if editor_role == "float":
            editor = QDoubleSpinBox(parent)
            editor.setFrame(False)
            editor.setDecimals(2)
            editor.setSingleStep(0.1)
            return editor
        if editor_role == "float_slider":
            editor = SliderWithValue(parent)
            editor.slider.setOrientation(Qt.Horizontal)
            editor.model_index = index
            def set_model_data(v):
                editor.model_index.model().setData(editor.model_index, v)
            editor.sliderMoved.connect(set_model_data)
            index.model().setData(index, editor, Roles.PersistentEditorWidgetRole)
            editor.sliderReleased.connect(lambda: self.commitData.emit(editor))
            return editor
        if editor_role == "color":
            editor = QColorDialog(parent)
            editor.setModal(True)
            return editor
        if editor_role == "colormap":
            editor = RasterLayerColorMapEditor(parent)
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        editor_role: Optional[str] = index.data(Roles.EditorRole)
        if editor_role == "integer":
            assert isinstance(editor, QSpinBox)
            value, name, vmin, vmax, unit = index.data(Qt.ItemDataRole.EditRole)
            editor.setValue(value)
            editor.setPrefix(f"{name} : ")
            if vmin is not None:
                editor.setMinimum(vmin)
            if vmax is not None:
                editor.setMaximum(vmax)
            if unit:
                editor.setSuffix(f" {unit}")
        elif editor_role == "float":
            assert isinstance(editor, QDoubleSpinBox)
            value, name, vmin, vmax, unit = index.data(Qt.ItemDataRole.EditRole)
            editor.setValue(value)
            editor.setPrefix(f"{name} : ")
            if vmin is not None:
                editor.setMinimum(vmin)
            if vmax is not None:
                editor.setMaximum(vmax)
            if unit:
                editor.setSuffix(f" {unit}")
        elif editor_role == "float_slider":
            value, name, vmin, vmax = index.data(Qt.ItemDataRole.EditRole)
            if vmin is not None:
                editor.setMinimum(vmin)
            if vmax is not None:
                editor.setMaximum(vmax)
            dataset = index.model().data(index.parent(), Roles.DatasetRole)
            def show_lat(v):
                x_d, y_d = dataset.xy(0.0, dataset.width * v)
                if dataset.crs is not None:
                    [x], [y] = rasterio.warp.transform(dataset.crs, rasterio.crs.CRS.from_epsg(4326),
                                                       [x_d], [y_d])
                else:
                    x, y = x_d, y_d
                return f"long: {x:0.03f}"
            editor.setDisplayValue(show_lat)
            editor.setValue(value)
        elif editor_role == "color":
            assert isinstance(editor, QColorDialog)
            color = index.data(Qt.ItemDataRole.EditRole)
            editor.setCurrentColor(color)
        elif editor_role == "colormap":
            assert isinstance(editor, RasterLayerColorMapEditor)
            layer = index.data(Qt.ItemDataRole.EditRole)
            editor.set_layer(layer)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        assert isinstance(model, ProxyLayerModel)
        index = model.mapToSource(index)
        model = model.sourceModel()
        assert isinstance(model, LayerModel)
        editor_role: Optional[str] = index.data(Roles.EditorRole)
        if editor_role == "integer":
            assert isinstance(editor, QSpinBox)
            editor.interpretText()
            model.add_undo_command.emit(SetDataCommand(
                model, index, int(editor.value()), Qt.ItemDataRole.EditRole))
        elif editor_role == "float":
            assert isinstance(editor, QDoubleSpinBox)
            editor.interpretText()
            model.add_undo_command.emit(SetDataCommand(
                model, index, float(editor.value()), Qt.ItemDataRole.EditRole))
        elif editor_role == "float_slider":
            model.add_undo_command.emit(SetDataCommand(
                model, index, float(editor.value()), Qt.ItemDataRole.EditRole,
                old_value = editor.initial_value
            ))
        elif editor_role == "color":
            assert isinstance(editor, QColorDialog)
            if editor.result() == QDialog.DialogCode.Accepted:
                color = editor.currentColor()
                model.add_undo_command.emit(SetDataCommand(model, index, color,
                                                           Qt.ItemDataRole.EditRole))
        elif editor_role == "colormap":
            assert isinstance(editor, RasterLayerColorMapEditor)
            if editor.result() == QDialog.DialogCode.Accepted:
                colormap = editor.get_colormap()
                v0, v1 = editor.get_v0_v1()
                model.add_undo_command.emit(SetDataCommand(model, index, (colormap, v0, v1),
                                                           Qt.ItemDataRole.EditRole))
        else:
            # base implementation of QStyledItemDelegate with model.setData replaced by
            # model.add_undo_command...
            n = editor.metaObject().userProperty().name()
            if n == "":
                n = str(self.itemEditorFactory().valuePropertyName(
                    model.data(index, Qt.ItemDataRole.EditRole).userType()))
            if n != "":
                model.add_undo_command.emit(SetDataCommand(
                    model, index, editor.property(n), Qt.ItemDataRole.EditRole))

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem,
                             index: QModelIndex) -> None:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        editor.setGeometry(option.rect)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        persistent_editor = index.model().data(index, int(Roles.PersistentEditorWidgetRole))
        if persistent_editor is not None:
            ret = persistent_editor.sizeHint()
            return ret
        return super().sizeHint(option, index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        display_role = index.data(Qt.ItemDataRole.DisplayRole)
        if display_role is None:
            persistent_editor = index.data(int(Roles.PersistentEditorWidgetRole))
            if persistent_editor is None:
                self.parent().openPersistentEditor(index)
            else:
                persistent_editor.model_index = index

        elif isinstance(display_role, QColor):
            self.initStyleOption(option, index)
            painter.save()
            color: QColor = index.data(Qt.ItemDataRole.DisplayRole)
            img = QImage(1, 1, QImage.Format.Format_RGBA8888)
            img.setPixelColor(0, 0, color)
            painter.drawImage(option.rect, img)
            painter.setBrush(QBrush())
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            painter.drawRect(option.rect.adjusted(0, 0, 0, -1))
            painter.restore()
        elif isinstance(display_role, ColorMap):
            self.initStyleOption(option, index)
            painter.save()
            colormap: ColorMap = index.data(Qt.ItemDataRole.DisplayRole)
            lut = colormap.getLookupTable(nPts=option.rect.width(), alpha=True)
            img = QImage(lut, len(lut), 1, QImage.Format.Format_RGBA8888)
            painter.drawImage(option.rect, img)
            painter.setBrush(QBrush())
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            painter.drawRect(option.rect.adjusted(0, 0, 0, -1))
            painter.restore()

        else:
            super().paint(painter, option, index)

    def eventFilter(self, editor: QObject, event: QEvent) -> bool:
        if isinstance(editor, (QColorDialog, RasterLayerColorMapEditor)):
            # tab is not used to move to the next element when editor is opened
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Tab or event.key() == Qt.Key.Key_Backtab:
                    return False
                elif (event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return or
                      event.key() == Qt.Key.Key_Escape):
                    return False
            # prevent editor to close when loosing focus (resize / alt+tab...)
            if event.type() == QEvent.Type.FocusOut:
                return False
        return super().eventFilter(editor, event)


# RemoveDelegate class #############################################################################

class RemoveDelegate(QStyledItemDelegate):

    clicked = Signal(QModelIndex)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.remove_icon = QIcon('icons:remove.png')

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if not index.isValid():
            return None
        self.initStyleOption(option, index)
        if not option.state & QStyle.StateFlag.State_Selected:
            return None
        if not index.flags() & Qt.ItemFlag.ItemIsEditable:
            # if item is not deletable
            return None
        if option.widget:
            style = option.widget.style()
        else:
            app = QApplication.instance()
            assert isinstance(app, QApplication)
            style = app.style()
        widget = option.widget
        style.drawControl(QStyle.ControlElement.CE_PushButton, self.button_option(option), painter,
                          widget)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        editor = QPushButton(parent)
        editor.setFlat(True)
        editor.setIcon(self.remove_icon)
        editor.setToolTip("Remove")
        editor.clicked.connect(lambda: self.clicked.emit(index))
        return editor

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        # iconsize + 8 pixels vertically (4 above and 4 under)
        button_option = self.button_option(option)
        return button_option.iconSize + QSize(0, 8)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem,
                             index: QModelIndex) -> None:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        editor.setGeometry(option.rect)

    def button_option(self, option: QStyleOptionViewItem) -> QStyleOptionButton:
        # see https://forum.qt.io/topic/131602/set-delegate-for-each-cell-in-a-qtablewidget/21
        button_option = QStyleOptionButton()
        button_option.rect = option.rect
        button_option.icon = self.remove_icon
        if option.widget:
            style = option.widget.style()
        else:
            app = QApplication.instance()
            assert isinstance(app, QApplication)
            style = app.style()
        size = style.pixelMetric(QStyle.PixelMetric.PM_ButtonIconSize, option)
        button_option.iconSize = QSize(size, size)
        button_option.palette = option.palette
        button_option.features = (QStyleOptionButton.ButtonFeature.None_ |
                                  QStyleOptionButton.ButtonFeature.Flat)
        button_option.state = option.state
        return button_option
