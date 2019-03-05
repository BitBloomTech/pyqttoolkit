#pylint: disable=no-name-in-module
from PyQt5.Qt import pyqtSignal, Qt
from PyQt5.QtWidgets import QLineEdit
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.views.styleable import make_styleable

class LineEdit(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.focusLost.connect(self._on_edit_complete)
        self.enterPressed.connect(self._on_edit_complete)

    focusLost = pyqtSignal()
    enterPressed = pyqtSignal()
    editComplete = pyqtSignal(str)

    def focusOutEvent(self, event):
        self.focusLost.emit()
        QLineEdit.focusOutEvent(self, event)
    
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.enterPressed.emit()
        QLineEdit.keyPressEvent(self, event)

    def _on_edit_complete(self):
        self.editComplete.emit(self.text())

class BindableLineEdit(LineEdit):
    def __init__(self, parent):
        LineEdit.__init__(self, parent)
        self.editComplete.connect(self._update_value)
        self.valueChanged.connect(self._handle_value_changed)
    
    valueChanged = pyqtSignal(str)

    value = AutoProperty(str)
    
    def _update_value(self, value):
        self.value = value
    
    def _handle_value_changed(self, value):
        self.setText(value)

BindableLineEdit = make_styleable(BindableLineEdit)