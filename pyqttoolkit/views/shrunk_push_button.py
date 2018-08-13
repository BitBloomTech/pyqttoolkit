#pylint: disable=no-name-in-module
from PyQt5.Qt import QSize
from PyQt5.QtWidgets import QPushButton
#pylint: enable=no-name-in-module

class ShrunkPushButton(QPushButton):
    def __init__(self, text, parent):
        QPushButton.__init__(self, text, parent)

    def sizeHint(self):
        return QSize(self.fontMetrics().width(self.text()) + 10, QPushButton.sizeHint(self).height())

class VShrunkPushButton(ShrunkPushButton):
    def __init__(self, text, parent):
        ShrunkPushButton.__init__(self, text, parent)
        self.setFixedHeight(22)
