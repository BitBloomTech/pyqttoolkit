#pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject
#pylint: enable=no-name-in-module

class ValidationModel(QObject):
    def __init__(self, parent, error):
        QObject.__init__(self, parent)
        self._error = error

    @property
    def error(self):
        return self._error
