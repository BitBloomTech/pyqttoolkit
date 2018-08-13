#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class CodeTextModel(QObject):
    def __init__(self, parent, validator):
        QObject.__init__(self, parent)
        self.textChanged.connect(self._validate)
        self._validator = validator
        self.text = ''

    textChanged = pyqtSignal(str)
    validationMessageChanged = pyqtSignal(str)

    text = AutoProperty(str)
    validationMessage = AutoProperty(str)

    def _validate(self, value):
        validation_model = self._validator(value)
        self.validationMessage = validation_model.error if validation_model else ''
