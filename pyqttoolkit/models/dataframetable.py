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
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QAbstractTableModel, Qt, QVariant, QModelIndex, QItemSelectionModel
#pylint: enable=no-name-in-module

class DataFrameTableModel(QAbstractTableModel):
    def __init__(self, parent, data, display_column=None, editable=False, row_headers=False):
        QAbstractTableModel.__init__(self, parent)
        self._data = data.copy()
        self._display_column_index = (
            0 if display_column is None
            else data.columns.get_loc(display_column)
        )
        self._selection_model = QItemSelectionModel(self)
        self._editable = editable
        self._row_headers = row_headers

    dataUpdated = pyqtSignal()

    def data(self, index, role=Qt.DisplayRole):
        if role in [Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole]:
            column = self._data.columns[index.column()]
            return str(self._data[column].iloc[index.row()])
        return QVariant()
    
    def headerData(self, section, orientation, role=None):
        role = role or Qt.DisplayRole
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            elif self._row_headers:
                return str(self._data.index[section])
        return None
    
    def flags(self, _index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if self._editable:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            column = self._data.columns[index.column()]
            self._data[column][index.row()] = value
            self.dataUpdated.emit()
            return True
        return False

    def columnCount(self, _parent=None):
        return len(self._data.columns)

    def rowCount(self, _parent=None):
        return len(self._data)

    def insertRows(self, row, count, parent=None, gen_row=None):
        parent = parent or QModelIndex()
        if row != self.rowCount(parent):
            return False
        if count != 1:
            raise ValueError('Cannot insert more than 1 row')

        gen_row = gen_row or (lambda: {n: '' for n in self._data.columns})

        self.beginInsertRows(parent, row, row)
        self._data.loc[row] = gen_row()
        self.dataUpdated.emit()
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=None):
        parent = parent or QModelIndex()
        if count != 1:
            raise ValueError('Cannot remove more than 1 row')
        
        self.beginRemoveRows(parent, row, row)
        self._data.drop(row, inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.dataUpdated.emit()
        self.endRemoveRows()
        return True

    def moveRows(self, source_parent, source_row, count, dest_parent, dest_row):
        if count != 1:
            raise ValueError('Cannot move more than 1 row')
        dest_row = min(dest_row, len(self._data) - 1)
        dest_row = max(dest_row, 0)
        if dest_row == source_row:
            return False
        self.beginMoveRows(source_parent, source_row, source_row + count, dest_parent, dest_row)
        temp = self._data.iloc[dest_row].copy()
        self._data.iloc[dest_row] = self._data.iloc[source_row]
        self._data.iloc[source_row] = temp
        self.endMoveRows()
        self.dataUpdated.emit()
        self.selectionModel.setCurrentIndex(self.createIndex(dest_row, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        return True

    def removeSelected(self):
        selected_rows = {i.row() for i in self._selection_model.selectedIndexes()}
        if len(selected_rows) > 1:
            raise ValueError('Removal of more than one row not currently supported')
        for row in selected_rows:
            self.removeRows(row, 1)

    @property
    def dataFrame(self):
        return self._data

    @dataFrame.setter
    def dataFrame(self, value):
        if self._data.size != value.size or not (self._data == value).all().all():
            self.beginResetModel()
            self._data = value.copy()
            self.endResetModel()

    @property
    def displayColumnIndex(self):
        return self._display_column_index

    @property
    def selectionModel(self):
        return self._selection_model
