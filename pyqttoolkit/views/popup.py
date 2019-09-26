#pylint: disable=no-name-in-module
from PyQt5.Qt import QFrame, QPoint, Qt, QGridLayout
#pylint: enable=no-name-in-module

class Popup(QFrame):
    def __init__(self, parent, contents):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Popup)
        self.setFrameStyle(QFrame.WinPanel | QFrame.Raised)
        self._contents = contents
        self._layout = QGridLayout(self)
        self._layout.addWidget(contents, 0, 0)
    
    def popupAtPosition(self, parent, rect):
        self.show()
        new_pos = parent.mapToGlobal(rect.bottomRight() - QPoint(self.width(), 0))
        new_pos = QPoint(max(0, new_pos.x()), new_pos.y())
        self.move(new_pos)

    @property
    def contents(self):
        return self._contents