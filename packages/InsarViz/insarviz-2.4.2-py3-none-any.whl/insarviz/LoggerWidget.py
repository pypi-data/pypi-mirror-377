import logging

from PySide6.QtWidgets import (
    QTableView, QHeaderView
)
from PySide6.QtGui import (
    QColor, QStandardItemModel, QStandardItem
)
from PySide6.QtCore import (
    Qt, QObject, Signal, Slot,
    QAbstractItemModel, QModelIndex
)

class LogsStoreSignals(QObject):
    new_record = Signal()
class LogsStore(logging.Handler):
    def __init__(self):
        super().__init__()
        self._records = []
        self._signals = LogsStoreSignals()

    @property
    def records(self):
        return self._records
    @property
    def new_record(self):
        return self._signals.new_record

    def emit(self, record):
        self._records.append(record)
        self.new_record.emit()

class LogsItemModel(QAbstractItemModel):
    def __init__(self, log_store):
        super().__init__()
        self._log_store = log_store
        self._log_store.new_record.connect(self._on_new_record)

    @Slot()
    def _on_new_record(self):
        size = len(self._log_store.records)
        self.beginInsertRows(QModelIndex(), size-1, size-1)
        self.endInsertRows()

    def rowCount(self, index):
        if index.isValid():
            return 0
        else:
            return len(self._log_store.records)
    def columnCount(self, index):
        return 4

    def parent(self, index):
        return QModelIndex()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                match section:
                    case 0:
                        return "Log level"
                    case 1:
                        return "Source"
                    case 2:
                        return "Function"
                    case 3:
                        return "Message"
        else:
            if role == Qt.ItemDataRole.DisplayRole:
                return str(section)
        return None

    def data(self, index, role):
        if index.isValid():
            record = self._log_store.records[index.row()]
            if role == Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case 0:
                        return record.levelname
                    case 1:
                        return record.name
                    case 2:
                        return record.funcName
                    case 3:
                        return record.message

            if role == Qt.ItemDataRole.ForegroundRole:
                match record.levelno:
                    case logging.WARNING:
                        return QColor('orange')
                    case logging.ERROR:
                        return QColor('red')
                    case logging.DEBUG:
                        return QColor('grey')
                return None
            return None

    def index(self, row, column, parent):
        return self.createIndex(row, column, None)

class LoggerWidget(QTableView):
    def __init__(self, log_store):
        super().__init__()
        self.setModel(LogsItemModel(log_store))
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
