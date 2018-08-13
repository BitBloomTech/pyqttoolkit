#pylint: disable=no-name-in-module
from PyQt5.Qt import QTreeView
#pylint: enable=no-name-in-module

class PropertyTreeView(QTreeView):
    def __init__(self, parent):
        QTreeView.__init__(self, parent)
    
    def resizeEvent(self, event):
        width = event.size().width()
        self.setColumnWidth(0, width * 0.5)
        self.setColumnWidth(1, width * 0.5)
