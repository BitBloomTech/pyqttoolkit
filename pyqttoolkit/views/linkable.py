#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget
#pylint: enable=no-name-in-module

class LinkableWidget(QWidget):
    def __init__(self, parent, link_manager=None):
        QWidget.__init__(self, parent)
        self._link_display = None
        self._link_manager = link_manager
    
    def linkDisplay(self):
        return self._link_display or self
    
    def setLinkDisplay(self, value):
        self._link_display = value

    def mouseDoubleClickEvent(self, _event):
        self.linkRequested()
    
    def linkRequested(self):
        if self._link_manager is not None:
            self._link_manager.request_link(self)
    
    def link(self, other):
        raise NotImplementedError()

    def unlink(self, other):
        raise NotImplementedError()
