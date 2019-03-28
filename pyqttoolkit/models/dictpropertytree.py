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
from enum import Enum

#pylint: disable=no-name-in-module
from PyQt5.Qt import Qt, QAbstractItemModel, pyqtSignal, QModelIndex, QVariant
#pylint: enable=no-name-in-module

class DictPropertyTreeModel(QAbstractItemModel):
    def __init__(self, parent, data):
        QAbstractItemModel.__init__(self, parent)
        self._data = data
        self._nodes = []
        self._indexes = {}
    
    propertyChanged = pyqtSignal(object, object)

    @property
    def value(self):
        return self._data
    
    @value.setter
    def value(self, value):
        self._data = value
        start_index = self.createIndex(0, 0)
        end_index = self.createIndex(self.rowCount(), self.columnCount())

        self.dataChanged.emit(start_index, end_index)
    
    def rowCount(self, parent=None):
        keys = self._keys(parent)
        return len(keys) if keys else 0
    
    def columnCount(self, _parent=None):
        return 2
    
    def parent(self, index):
        return self._nodes[index.internalId()] if index.isValid() else QModelIndex()
    
    def hasChildren(self, index):
        return isinstance(self._property_type(index), dict)
    
    def index(self, row, column, parent):
        if (row, column, parent) not in self._indexes:
            internal_id = len(self._nodes)
            self._nodes.append(parent)
            self._indexes[(row, column, parent)] = self.createIndex(row, column, internal_id)
        return self._indexes[(row, column, parent)]
    
    def flags(self, index):
        if index.column() == 0 or isinstance(self._property_type(index), dict):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role=None):
        role = role or Qt.DisplayRole
        if role in [Qt.DisplayRole, Qt.EditRole]:
            if index.column() == 0:
                return self._property_name(index)
            data = self._properties(index)
            if isinstance(data, dict):
                return None
            return data and self._property_type(index)(data)
        return None
    
    def setData(self, index, value, role=None):
        role = role or Qt.EditRole
        if role == Qt.EditRole:
            if index.column() == 1:
                self._set_property(index, value)
                return True
        return False
    
    def headerData(self, section, orientation, role=None):
        role = role or Qt.DisplayRole
        if role in [Qt.DisplayRole, Qt.EditRole] and orientation in [Qt.Horizontal]:
            return self.tr('Property Name') if section == 0 else self.tr('Property Value')
        return QVariant()

    def _keys(self, parent=None):
        types = self._property_type(parent)
        return self._sort_keys(types) if isinstance(types, dict) else None
    
    def _properties(self, index):
        properties = self._data
        for property_ in self._property_path(index):
            if properties is None:
                break
            properties = properties.get(property_.name, None)
        return properties
    
    def _set_property(self, index, value):
        property_path = self._property_path(index)
        properties = self._data
        for property_ in property_path[:-1]:
            properties = properties.setdefault(property_.name, {})
        type_ = self._property_type(index)
        try:
            value = type_(value)
        except ValueError:
            value = properties.get(property_path[-1].name)
        properties[property_path[-1].name] = value
        self.propertyChanged.emit(property_path[-1], value)
    
    def _property_name(self, index):
        property_path = self._property_path(index)
        property_enum = property_path[-1]
        return self.propertyNames.get(property_enum, property_enum.name)
    
    def _property_key(self, properties, index):
        return self._sort_keys(properties)[index.row()]
    
    def _property_type(self, index):
        types = self.propertyTypes
        for property_ in self._property_path(index):
            types = types[property_]
        return types
    
    def _property_path(self, parent):
        ancestors = []
        while parent is not None and parent.isValid():
            ancestors.insert(0, parent)
            parent = self.parent(parent)
        properties = self.propertyTypes
        property_path = []
        for ancestor in ancestors:
            property_keys = self._sort_keys(properties)
            current_property = property_keys[ancestor.row()]
            properties = properties[current_property]
            property_path.append(current_property)
        return property_path
    
    @property
    def propertyNames(self):
        raise NotImplementedError()
    
    @property
    def propertyTypes(self):
        raise NotImplementedError()

    @staticmethod
    def _sort_keys(dict_):
        return list(sorted(dict_.keys(), key=lambda v: v.value if isinstance(v, Enum) else v))
