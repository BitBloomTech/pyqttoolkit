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
from PyQt5.QtCore import pyqtSignal, QItemSelectionModel
from PyQt5.Qt import QWidget, QGridLayout, QAbstractItemModel, QStringListModel, Qt
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import auto_property
from pyqttoolkit.models.roles import DataRole
from .list_view import ListView

class BulkValueSelectorWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._value_selector = ListView(self)
        self._value_selector.setSelectionMode(ListView.ExtendedSelection)
        self._value_selector.selectedItemsChanged.connect(lambda: self.selectedValuesChanged.emit(self.selectedValues))

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._value_selector)
        self.setLayout(self._layout)

    valuesChanged = pyqtSignal(QAbstractItemModel)
    selectedValuesChanged = pyqtSignal(list)
    dataCommitted = pyqtSignal(list)

    @auto_property(QAbstractItemModel)
    def values(self):
        return self._value_selector.model()
    
    @values.setter
    def values(self, value):
        self._value_selector.setModel(value)
        self._value_selector.selectAll()
        self.valuesChanged.emit(value)
        self.selectedValuesChanged.emit(self.selectedValues)

    def setValues(self, values):
        self.values = values
        values.dataChanged.connect(self._handle_values_changed)
        if hasattr(values, 'selectionModel'):
            self._value_selector.setSelectionModel(values.selectionModel)
    
    def selectAll(self):
        self._value_selector.selectAll()
    
    @auto_property(list)
    def selectedValues(self):
        if isinstance(self._value_selector.model(), QStringListModel):
            return [
                self._value_selector.model().stringList()[i.row()]\
                    for i in self._value_selector.selectedIndexes() if i.row() < self._value_selector.model().rowCount()
            ]
        return [self._value_selector.model().data(i, DataRole) for i in self._value_selector.selectedIndexes() if i.row() < self._value_selector.model().rowCount()]
    
    @selectedValues.setter
    def selectedValues(self, values):
        select_values = (
            self._select_values_stringlist if isinstance(self._value_selector.model(), QStringListModel) 
            else self._select_values if self._value_selector.model()
            else None
        )
        if select_values:
            signals_blocked = self.blockSignals(True)
            self._value_selector.clearSelection()
            select_values(values)
            self.blockSignals(signals_blocked)
            self.selectedValuesChanged.emit(self.selectedValues)
    
    def _select_values_stringlist(self, values):
        for value in values:
            index = self._value_selector.model().stringList().index(value)
            model_index = self._value_selector.model().createIndex(index, 0)
            self._value_selector.selectionModel().setCurrentIndex(model_index, QItemSelectionModel.Rows | QItemSelectionModel.Select)
    
    def _select_values(self, values):
        model = self._value_selector.model()
        for i in range(model.rowCount()):
            model_index = model.createIndex(i, 0)
            data = model.data(model_index, DataRole)
            if data in values:
                self._value_selector.selectionModel().setCurrentIndex(model_index, QItemSelectionModel.Rows | QItemSelectionModel.Select)

    def _handle_values_changed(self):
        self.selectedValuesChanged.emit(self.selectedValues)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.dataCommitted.emit(self.selectedValues)