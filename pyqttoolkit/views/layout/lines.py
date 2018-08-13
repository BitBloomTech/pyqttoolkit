#pylint: disable=no-name-in-module
from PyQt5.Qt import QFrame
#pylint: enable=no-name-in-module

class HLine(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class VLine(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
