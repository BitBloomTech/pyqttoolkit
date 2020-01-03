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
""":mod:`combo_box`
Defines the ComboBox class
"""
from enum import Enum

#pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QComboBox
from PyQt5.Qt import pyqtSignal
from PyQt5.QtCore import Qt
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.models.roles import DataRole
from pyqttoolkit.views.styleable import make_styleable

class ComboBox(QComboBox):
    def __init__(self, parent, padding=20):
        QComboBox.__init__(self, parent)
        self.setMaxVisibleItems(20)
        self.setMinimumWidth(50)
        self.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.view().setTextElideMode(Qt.ElideNone)
        self._padding = padding
    
    def setModel(self, value):
        QComboBox.setModel(self, value)
        self._update_minimum_width()
        value.dataChanged.connect(self._update_minimum_width)
    
    def _update_minimum_width(self):
        width = self.minimumWidth()
        if self.model():
            for i in range(self.model().rowCount()):
                index = self.model().createIndex(i, 0)
                display_text = self.model().data(index, Qt.DisplayRole)
                width = max(width, self.fontMetrics().width(display_text))
            self.view().setMinimumWidth(width + self._padding)

ComboBox = make_styleable(ComboBox)

def typed_bindable_combo_box(type_):
    class TypedBindableComboBox(ComboBox):
        def __init__(self, parent):
            ComboBox.__init__(self, parent)

            self.currentIndexChanged.connect(self._handle_index_changed)
            self.valueChanged.connect(self._update_index)
        
        valueChanged = pyqtSignal(type_)

        value = AutoProperty(type_)

        def setModel(self, value):
            super().setModel(value)
            if hasattr(value, 'dataChanged'):
                value.dataChanged.connect(self._handle_data_changed)
        
        def _handle_data_changed(self):
            self._update_index(self.value)
            self._handle_index_changed(self.currentIndex())

        def _handle_index_changed(self, index):
            if 0 <= index < self.model().rowCount():
                model_index = self.model().createIndex(index, 0)
                self.value = self._get_data_value(model_index)

        def _update_index(self, value):
            index = self._get_index(value)
            index = index if index is not None else 0
            if 0 <= index < self.model().rowCount():
                self.setCurrentIndex(index)

        
        def _get_index(self, value):
            for i in range(self.model().rowCount()):
                model_index = self.model().createIndex(i, 0)
                if self._get_data_value(model_index) == value:
                    return i
            return None

        def _get_data_value(self, model_index):
            value = self.model().data(model_index, DataRole)
            value = value if value is not None else self.model().data(model_index, Qt.DisplayRole)
            return value if not isinstance(value, Enum) else value.name
    
    return make_styleable(TypedBindableComboBox)

BindableComboBox = typed_bindable_combo_box(str)
