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
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.views import LineEdit

class DefaultTextLineEdit(LineEdit):
    def __init__(self, parent):
        LineEdit.__init__(self, parent)
        self.editComplete.connect(self._update_name)
        self.nameChanged.connect(self._handle_name_changed)
        self.defaultNameChanged.connect(self._handle_name_changed)
    
    defaultNameChanged = pyqtSignal(str)
    nameChanged = pyqtSignal(str)

    defaultName = AutoProperty(str)
    name = AutoProperty(str)

    def focusInEvent(self, event):
        self._handle_interaction()
        LineEdit.focusInEvent(self, event)

    def _update_name(self, value):
        self.name = value

    def _handle_name_changed(self):
        self.setText(self.name)
        if not self.name:
            self.setPlaceholderText(self.defaultName)

    def _handle_interaction(self):
        if not self.name:
            self.name = self.defaultName
