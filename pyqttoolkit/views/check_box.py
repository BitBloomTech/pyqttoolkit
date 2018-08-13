#pylint: disable=no-name-in-module
from PyQt5.Qt import QCheckBox, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class BindableCheckBox(QCheckBox):
    def __init__(self, label, parent):
        QCheckBox.__init__(self, label, parent)
        self.clicked.connect(self._handle_clicked)
        self.checkedChanged.connect(self.setChecked)
    
    checkedChanged = pyqtSignal(bool)

    checked = AutoProperty(bool)

    def _handle_clicked(self):
        self.checked = self.isChecked()
