#pylint: disable=no-name-in-module
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
