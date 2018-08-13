#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget, QStyleOption, QStyle, QPainter
#pylint: enable=no-name-in-module

class StyleableWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
    def paintEvent(self, _event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
