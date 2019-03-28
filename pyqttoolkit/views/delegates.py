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
from PyQt5.Qt import QItemDelegate
#pylint: enable=no-name-in-module

from pyqttoolkit.models.roles import DataRole
from pyqttoolkit.views import BindableComboBox

class ComboBoxItemDelegate(QItemDelegate):
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)
    
    def setComboBoxModel(self, model):
        self._combo_box_model = model
    
    def createEditor(self, parent, option, index):
        combo_box = BindableComboBox(parent)
        combo_box.setModel(self._combo_box_model)
        value = self.parent().model().data(index, DataRole)
        if isinstance(value, Enum):
            value = value.name
        combo_box.value = value
        combo_box.currentIndexChanged.connect(self.closeEditor(combo_box))
        return combo_box
    
    def setEditorData(self, editor, index):
        editor.showPopup()

    def closeEditor(self, control):
        def _handler():
            self.parent().commitData(control)
            self.parent().closeEditor(control, QItemDelegate.NoHint)
        return _handler
