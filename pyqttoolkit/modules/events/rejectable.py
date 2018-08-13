#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject
#pylint: enable=no-name-in-module

class RejectableEvent(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._accepted = True
    
    @property
    def accepted(self):
        return self._accepted
    
    def reject(self):
        self._accepted = False
