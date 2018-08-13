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

class BindableComboBox(ComboBox):
    def __init__(self, parent):
        ComboBox.__init__(self, parent)

        self.currentIndexChanged.connect(self._handle_index_changed)
        self.valueChanged.connect(self._update_index)
    
    valueChanged = pyqtSignal(str)

    value = AutoProperty(str)
    
    def _handle_index_changed(self, index):
        if index < self.model().rowCount():
            model_index = self.model().createIndex(index, 0)
            self.value = self._get_data_value(model_index)

    def _update_index(self, value):
        for i in range(self.model().rowCount()):
            model_index = self.model().createIndex(i, 0)
            if self._get_data_value(model_index) == value:
                self.setCurrentIndex(i)
                return
            
    def _get_data_value(self, model_index):
        value = self.model().data(model_index, DataRole)
        value = value if value is not None else self.model().data(model_index, Qt.DisplayRole)
        return value if not isinstance(value, Enum) else value.name
