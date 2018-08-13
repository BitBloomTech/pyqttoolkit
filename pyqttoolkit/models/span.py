#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject
#pylint: enable=no-name-in-module

class SpanModel(QObject):
    def __init__(self, parent, left, right):
        QObject.__init__(self, parent)
        self._left = left
        self._right = right
    
    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right
