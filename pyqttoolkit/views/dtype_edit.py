from math import isnan, isfinite

#pylint: disable=no-name-in-module
from PyQt5.Qt import QDoubleValidator, pyqtSignal
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
    def __init__(self, parent):
        LineEdit.__init__(self, parent)
        self.editComplete.connect(self._handle_edit_complete)
        self.valueChanged.connect(self._handle_value_changed)
    
    valueChanged = pyqtSignal(float)
    value = AutoProperty(float)

    def _handle_edit_complete(self):
        try:
            self.value = float(self.text())
        except ValueError:
            self.setText(str(self.value))
    
    def _handle_value_changed(self, value):
        self.setText(str(value))
    
class AutoFloatLineEdit(InfFloatLineEdit):
    def __init__(self, parent, allow_inf=True):
        InfFloatLineEdit.__init__(self, parent)
        self._allow_inf = allow_inf

    @property
    def _auto(self):
        return self.tr('Auto')
    
    def _handle_edit_complete(self):
        if self.text().lower() == self._auto.lower() and not isnan(self.value):
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
        self.setText(self._auto)
    
    def _handle_value_changed(self, value):
        if isnan(value):
            self.setText(self._auto)
        else:
            InfFloatLineEdit._handle_value_changed(self, value)

    def setText(self, value):
        InfFloatLineEdit.setText(self, self._auto if value == 'nan' else value)
