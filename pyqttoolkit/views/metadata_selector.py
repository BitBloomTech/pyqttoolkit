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
from PyQt5.Qt import QWidget, pyqtSignal, QGridLayout, QSizePolicy, QHBoxLayout, QSize
#pylint: enable=no-name-in-module

from pyqttoolkit.models.roles import DataRole
from pyqttoolkit.views import ComboBox
from pyqttoolkit.properties import AutoProperty, bind
from .icon_button import IconButton

class MetadataSelectorDropDown(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._drop_down = ComboBox(self)
        self._drop_down.currentIndexChanged.connect(self._update_current)
        
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._drop_down)

        self.selectedIdChanged.connect(self._handle_selected_id_changed)
        self.selectedId = None

    selectedIdChanged = pyqtSignal(str)

    selectedId = AutoProperty(str)

    def setModel(self, model):
        self._drop_down.setModel(model)
        model.dataChanged.connect(self._handle_selected_id_changed)

    def _update_current(self, index):
        model_index = self._drop_down.model().createIndex(index, 0)
        self.selectedId = self._drop_down.model().data(model_index, DataRole)

    def _handle_selected_id_changed(self):
        model = self._drop_down.model()
        for i in range(model.rowCount()):
            model_index = model.createIndex(i, 0)
            if model.data(model_index, DataRole) == self.selectedId:
                self._drop_down.setCurrentIndex(i)
                return

class MetadataSelector(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._drop_down = MetadataSelectorDropDown(self)
        self._drop_down.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._add_item = IconButton('plus.svg', self.tr('Add Item'), self, QSize(20, 20), 2)
        self._add_item.clicked.connect(self.addItemSelected)
   
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._drop_down)
        self._layout.addWidget(self._add_item)

        bind(self, self._drop_down, 'selectedId')
    
    selectedIdChanged = pyqtSignal(str)
    addItemSelected = pyqtSignal()

    selectedId = AutoProperty(str)
    
    def setModel(self, model):
        self._drop_down.setModel(model)

    def setSelectorEnabled(self, enabled):
        self._drop_down.setEnabled(enabled)
