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
