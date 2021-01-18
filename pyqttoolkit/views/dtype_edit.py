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
from math import isnan, isfinite

#pylint: disable=no-name-in-module
from PyQt5.Qt import QDoubleValidator, pyqtSignal, Qt
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.views import LineEdit

def _type_editor(dtype, default_value):
    class _TypeEdit(LineEdit):
        def __init__(self, parent):
            LineEdit.__init__(self, parent)
            self.setValidator(QDoubleValidator())
            self.editComplete.connect(self._set_value)
            self.valueChanged.connect(self._set_text)
        
        valueChanged = pyqtSignal(dtype)

        value = AutoProperty(dtype)

        def _set_value(self, text):
            try:
                self.value = dtype(text)
            except (TypeError, ValueError):
                self.value = default_value
                self._set_text(self.value)
        
        def _set_text(self, value):
            self.setText(str(value))
    
    return _TypeEdit

FloatEdit = _type_editor(float, 0.0)
IntEdit = _type_editor(int, 0)

class InfFloatLineEdit(LineEdit):
    def __init__(self, parent, formatter=None, update_on_enter_pressed=True):
        LineEdit.__init__(self, parent)
        self.editComplete.connect(self._handle_edit_complete)
        self.valueChanged.connect(self._handle_value_changed)
        self._formatter = formatter
        self._update_on_enter_pressed = update_on_enter_pressed
    
    valueChanged = pyqtSignal(float)
    value = AutoProperty(float)

    def _handle_edit_complete(self):
        try:
            self.value = float(self.text())
        except ValueError:
            self.setText(self._get_text(self.value))
    
    def _handle_value_changed(self, value):
        self.setText(self._get_text(value))

    def _get_text(self, value):
        if self._formatter is not None:
            return self._formatter(value)
        else:
            return str(value)
            
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in [Qt.Key_Enter, Qt.Key_Return] and self._update_on_enter_pressed:
            self.valueChanged.emit(self.value)


class AutoFloatLineEdit(InfFloatLineEdit):
    def __init__(self, parent, allow_inf=True, default_text=None, formatter=None, update_on_enter_pressed=True):
        InfFloatLineEdit.__init__(self, parent, formatter, update_on_enter_pressed)
        self._allow_inf = allow_inf
        self._default_text_ = default_text or self.tr('Auto')

    @property
    def _default_text(self):
        return self._default_text_
    
    def _handle_edit_complete(self):
        if self.text().lower() == self._default_text.lower() or not self.text():
            self._reset()
        else:
            if not self._allow_inf:
                try:
                    if not isfinite(float(self.text())):
                        self._reset()
                except ValueError:
                    pass
            InfFloatLineEdit._handle_edit_complete(self)
    
    def _reset(self):
        self.value = float('nan')
        self.setText(self._default_text)
    
    def _handle_value_changed(self, value):
        if isnan(value):
            self.setText(self._default_text)
        else:
            InfFloatLineEdit._handle_value_changed(self, value)

    def setText(self, value):
        InfFloatLineEdit.setText(self, self._default_text if value == 'nan' else value)
