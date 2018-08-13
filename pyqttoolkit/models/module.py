#pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject
#pylint: enable=no-name-in-module

class ModuleModel(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
