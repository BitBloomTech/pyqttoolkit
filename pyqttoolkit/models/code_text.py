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
from PyQt5.QtCore import QObject, pyqtSignal

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.logs import LogStream

class CodeTextModel(QObject):
    def __init__(self, parent, validator):
        QObject.__init__(self, parent)
        self.textChanged.connect(self._validate)
        self._validator = validator
        self.text = ''
        self.output = LogStream(self._handle_output_buffer_changed)

    textChanged = pyqtSignal(str)
    outputChanged = pyqtSignal(LogStream)
    validationMessageChanged = pyqtSignal(str)

    text = AutoProperty(str)
    output = AutoProperty(LogStream)
    validationMessage = AutoProperty(str)

    def _validate(self, value):
        validation_model = self._validator(value)
        self.validationMessage = validation_model.error if validation_model else ''

    def _handle_output_buffer_changed(self):
        self.outputChanged.emit(self.output)
