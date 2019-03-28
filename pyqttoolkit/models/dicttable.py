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
from PyQt5.Qt import Qt, QAbstractTableModel, pyqtSignal, QModelIndex
#pylint: enable=no-name-in-module

from pyqttoolkit.models.roles import DataRole

class DictTableModel(QAbstractTableModel):
    def __init__(self, parent, value):
        if not isinstance(value, dict):
            raise TypeError('value must be dict')
        QAbstractTableModel.__init__(self, parent)
        self._value = value
        self._pasting = False
        self._pasted_properties = {}
    
    propertyChanged = pyqtSignal(str, object, object)
    propertiesChanged = pyqtSignal(object)

    @property
    def value(self):
        return self._value

    def setValue(self, value):
        if not isinstance(value, dict):
            raise TypeError('value must be dict')
        if self._value != value:
            new_rows = len(value.keys()) - len(self._value.keys())
            if new_rows > 0:
                self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + new_rows - 1)
            elif new_rows < 0:
                self.beginRemoveRows(QModelIndex(), self.rowCount() + new_rows, self.rowCount() - 1)
    
            self._value = value
            start_index = self.createIndex(0, 0)
            end_index = self.createIndex(self.rowCount(), self.columnCount())

            self.dataChanged.emit(start_index, end_index)

            if new_rows > 0:
                self.endInsertRows()
            elif new_rows < 0:
                self.endRemoveRows()

    def data(self, index, role=None):
        role = role or Qt.DisplayRole
        if role in [Qt.DisplayRole, Qt.EditRole]:
            value = self._value[self._ids[index.row()]].get(self.displayProperties[index.column()])
            if value is None:
                return None
            if role == Qt.DisplayRole and isinstance(value, float):
                return '{:0.2f}'.format(value)
            return value
        return None
    
    def setData(self, index, value, role=None):
        role = role or Qt.EditRole
        if role == Qt.EditRole:
            if index.row() >= self.rowCount() or index.column() >= self.columnCount():
                return False
            id_ = self._ids[index.row()]
            property_ = self.displayProperties[index.column()]
            type_ = self.valueTypes[self.propertyType[property_]]
            try:
                converted_value = type_(value)
                self._value[id_][property_] = converted_value
            except ValueError:
                return False
            if not self._pasting:
                self.dataChanged.emit(index, index)
                self.propertyChanged.emit(id_, self.propertyType[property_], converted_value)
            else:
                self._pasted_properties[(id_, self.propertyType[property_])] = converted_value
            return True
        return False
    
    def headerData(self, section, orientation, role=None):
        role = role or Qt.DisplayRole
        if role in [Qt.DisplayRole, DataRole]:
            if orientation == Qt.Vertical:
                return self._ids[section]
            else:
                return self.headings[self.propertyType[self.displayProperties[section]]]
        return None
    
    def beginPaste(self):
        self.blockSignals(True)
        self._pasting = True
    
    def endPaste(self, from_index, to_index):
        self._pasting = False
        self.blockSignals(False)
        self.dataChanged.emit(from_index, to_index)
        self.propertiesChanged.emit(self._pasted_properties)
        self._pasted_properties = {}
    
    def flags(self, _index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def columnCount(self, _parent=None):
        return len(self.displayProperties)
    
    def rowCount(self, _parent=None):
        return len(self._ids)
    
    @property
    def _ids(self):
        return list(sorted(self._value.keys()))

    @property
    def propertyType(self):
        raise NotImplementedError()
    
    @property
    def displayProperties(self):
        raise NotImplementedError()
    
    @property
    def valueTypes(self):
        raise NotImplementedError()
    
    @property
    def headings(self):
        raise NotImplementedError()
