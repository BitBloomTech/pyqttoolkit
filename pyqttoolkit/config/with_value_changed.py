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
from PyQt5.QtCore import pyqtSignal, QObject

class WithValueChangedConfiguration(QObject):
    def __init__(self, parent, inner):
        super().__init__(parent)
        self._inner = inner
    
    onValueChanged = pyqtSignal(str, object)
    
    def get_value(self, key):
        return self._inner.get_value(key)

    def set_value(self, key, value):
        self._inner.set_value(key, value)
        self.onValueChanged.emit(key, value)
