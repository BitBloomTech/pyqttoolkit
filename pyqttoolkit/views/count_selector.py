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
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.Qt import QWidget, QHBoxLayout, QScrollBar, QLineEdit, QIntValidator
#pylint: enable=no-name-in-module

class CountSelectorWidget(QWidget):
    def __init__(self, parent, minimum, maximum, initial=0):
        QWidget.__init__(self, parent)

        self._slider = QScrollBar(Qt.Horizontal, self)
        self._slider.setMinimum(minimum)
        self._slider.setMaximum(maximum)
        self._slider.setSingleStep(1)
        # self._slider.setTickInterval(1)

        self._linedit = QLineEdit(self)
        self._linedit.setValidator(QIntValidator(minimum, maximum, self))
        self._linedit.setMinimumWidth(20)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._slider, 4)
        self._layout.addWidget(self._linedit, 1)

        self._slider.valueChanged.connect(self._update_value)
        self._linedit.textChanged.connect(self._update_value)
        self._update_value(initial)
    
    valueChanged = pyqtSignal(int)
    
    def _update_value(self, value):
        value = int(value) if value else 0
        self.value = value
        self.valueChanged.emit(value)
    
    @property
    def value(self):
        return self._slider.value()
    
    @value.setter
    def value(self, value):
        if self._slider.value() != value:
            self._slider.setValue(value)
        self._linedit.setText(str(value))
