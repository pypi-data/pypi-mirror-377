#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapted from PyQt Editable Tree Model Example
https://doc.qt.io/qtforpython-6/examples/example_widgets_itemviews_editabletreemodel.html
"""

from __future__ import annotations

from typing import Any, Optional, Union, overload

import weakref

from PySide6.QtCore import QObject, QModelIndex, Qt, QAbstractItemModel


# TreeItem class ###################################################################################

class TreeItem(QObject):

    kind: str = "item"  # description of the class

    def __init__(self, parent: Optional[TreeItem] = None):
        super().__init__()
        self.name: str = ""
        self._parent_item: Optional[weakref.ReferenceType] = None
        self.parent_item = parent
        self.child_items: list[TreeItem] = []

    @property
    def parent_item(self) -> Optional[TreeItem]:
        if self._parent_item is None:
            return None
        return self._parent_item()

    @parent_item.setter
    def parent_item(self, item: Optional[TreeItem]):
        # use weakref to prevent circular references between item and its parent that would prevent
        # garbage collection (we want to delete the textures of layers for example)
        if item is not None:
            self._parent_item = weakref.ref(item)

    def parent(self) -> Optional[TreeItem]:
        return self.parent_item

    def child(self, number: int) -> Optional[TreeItem]:
        if number < 0 or number >= len(self.child_items):
            return None
        return self.child_items[number]

    def last_child(self) -> Optional[TreeItem]:
        return self.child_items[-1] if self.child_items else None

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item is not None:
            return self.parent_item.child_items.index(self)
        return 0

    def data(self, column: int, role: int) -> Any:
        raise NotImplementedError

    def flags(self, flags: Qt.ItemFlags, column: int) -> Qt.ItemFlags:
        raise NotImplementedError

    def add_child(self, child: TreeItem, position: int = -1) -> bool:
        if position > len(self.child_items) or position < -1:
            return False
        elif position == -1:
            position = len(self.child_items)
        child.parent_item = self
        self.child_items.insert(position, child)
        return True

    def remove_children(self, position: int, count: int) -> bool:
        for _ in range(count):
            self.child_items.pop(position)
        return True

    def set_data(self, value, column: int, role: int) -> bool:
        raise NotImplementedError


# TreeModel class ##################################################################################

class TreeModel(QAbstractItemModel):
    # methods of the form methodName are inherited from QAbstractItemModel
    # methods of the form method_name are custom methods

    # WARNING removeRows(self, row, count, parent) SHOULD NOT BE DEFINED
    # (Qt tries to remove dragged rows but here they are just moved in the child_items list)

    # index of the remove column (column indexes start at 0, so the second column has index 1)
    remove_column: int = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = TreeItem()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        raise NotImplementedError

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        item: TreeItem = self.get_item(index)
        return item.data(index.column(), role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsDropEnabled
        item: TreeItem = self.get_item(index)
        return item.flags(QAbstractItemModel.flags(self, index), index.column())

    def get_item(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = index.internalPointer()
            if item:
                return item
        return self.root_item

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()
        item: Optional[TreeItem] = parent_item.child(row)
        if item is not None:
            return self.createIndex(row, column, item)
        return QModelIndex()

    # see https://mypy.readthedocs.io/en/stable/more_types.html#function-overloading
    @overload
    def parent(self, child: QModelIndex) -> QModelIndex: ...

    @overload
    def parent(self) -> QObject: ...

    def parent(self, child: Optional[QModelIndex] = None) -> Union[QObject, QModelIndex]:
        if child is None:
            return super().parent()
        if not child.isValid():
            return QModelIndex()
        item: TreeItem = self.get_item(child)
        parent_item: Optional[TreeItem]
        if item:
            parent_item = item.parent()
        else:
            parent_item = None
        if parent_item == self.root_item or parent_item is None:
            return QModelIndex()
        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        item: TreeItem = self.get_item(index)
        result: bool = item.set_data(value, index.column(), role)
        if result:
            self.dataChanged.emit(index, index, [role])
        return result

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        # DO NOT SUBCLASS
        return False

    # custom methods

    def add_item(self, item: 'TreeItem', row: int, parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False
        if row < -1 or row > self.rowCount(parent):
            return False
        if row == -1:
            row = self.rowCount(parent)
        self.beginInsertRows(parent, row, row)
        parent_item.add_child(item, row)
        self.endInsertRows()
        return True

    def move_item(self, start: int, target: int, parent: QModelIndex) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False
        if start == target:
            return True
        if target == parent_item.child_count() and start == target-1:
            # no need to move to the last row as it is already the last one
            return True
        self.beginMoveRows(parent, start, start, parent, target)
        if start < target:
            # item is removed before being added back, so if start < target that will
            # reduce the new position of target
            target -= 1
        item: TreeItem = parent_item.child_items.pop(start)
        parent_item.child_items.insert(target, item)
        self.endMoveRows()
        return True

    def remove_item(self, position: int, parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False
        if position < -1 or position + 1 > self.rowCount(parent):
            return False
        if position == -1:
            position = self.rowCount(parent) - 1
        self.beginRemoveRows(parent, position, position)
        parent_item.remove_children(position, 1)
        self.endRemoveRows()
        return True

    def clear(self) -> None:
        if self.rowCount():
            self.beginResetModel()
            self.root_item.remove_children(0, self.rowCount())
            self.endResetModel()
