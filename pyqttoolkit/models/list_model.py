# pyqttoolkit
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
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
            return (self._display_name_map.get(item) or item.name) if role == Qt.DisplayRole else item
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
