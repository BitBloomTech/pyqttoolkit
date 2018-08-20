#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class LauncherConfig(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.enabled = False

    enabledChanged = pyqtSignal(bool)

    enabled = AutoProperty(bool)
    
    @property
    def buttonTitle(self):
        return None
    
    @property
    def menuTitle(self):
        return None

    @property
    def buttonIcon(self):
        return None
    
    @property
    def menu(self):
        return None
    
    @property
    def order(self):
        return 0

    @property
    def alwaysEnabled(self):
        return False
