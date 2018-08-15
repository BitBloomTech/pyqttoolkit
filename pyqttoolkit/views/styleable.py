#pylint: disable=no-name-in-module
from PyQt5.Qt import QStyleOption, QStyle, QPainter
#pylint: enable=no-name-in-module

def _get_paintEvent(cls):
    def _paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        return cls.paintEvent(self, event)
    return _paintEvent

def make_styleable(cls):
    return type(
        cls.__name__,
        (cls,),
        {
            'paintEvent': _get_paintEvent(cls)
        }
    )
