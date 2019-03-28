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
from json import loads, dumps, JSONDecodeError

#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class JsonTextModel(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.textChanged.connect(self._set_data)
        self._data = {}
        self.text = '{}'

    textChanged = pyqtSignal(str)
    validationMessageChanged = pyqtSignal(str)

    text = AutoProperty(str)
    validationMessage = AutoProperty(str)

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self.text = dumps(
            value, sort_keys=True,
            indent=2, separators=(',', ': ')
        )

    def _set_data(self, value):
        try:
            self._data = loads(value)
            self.validationMessage = ''
        except JSONDecodeError:
            self.validationMessage = self.tr('Error in JSON')
