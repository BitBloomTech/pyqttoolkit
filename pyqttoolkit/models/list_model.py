#pylint: disable=no-name-in-module
from PyQt5.Qt import Qt, QAbstractListModel, QStringListModel
#pylint: enable=no-name-in-module

from pyqttoolkit.models.roles import DataRole

class ListModel(QAbstractListModel):
    def __init__(self, parent, items, display_name_map=None):
        QAbstractListModel.__init__(self, parent)
        self._items = items
        self._display_name_map = display_name_map or {}
    
    def rowCount(self, _parent=None):
        return len(self._items)
    
    def data(self, index, role=Qt.DisplayRole):
        if role in [Qt.DisplayRole, DataRole]:
            item = self._items[index.row()]
            return self._display_name_map.get(item, item.name) if role == Qt.DisplayRole else item
        return None
    
    @property
    def items(self):
        return self._items

class StringListModel(QStringListModel):
    def __init__(self, values):
        QStringListModel.__init__(self, values)
    
    def data(self, index, role):
        return QStringListModel.data(self, index, Qt.DisplayRole if role == DataRole else role)

class ToolTipStringListModel(StringListModel):
    def __init__(self, values):
        StringListModel.__init__(self, values)
    
    def data(self, index, role):
        return QStringListModel.data(self, index, Qt.DisplayRole if role == Qt.ToolTipRole else role)
