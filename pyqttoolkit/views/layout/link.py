from PyQt5.Qt import QWidget

class LinkWidget(QWidget):
    def __init__(self, parent, linkable_widget):
        super().__init__(parent)
        self._linkable_widget = linkable_widget
        if hasattr(self._linkable_widget, 'setLinkDisplay'):
            self._linkable_widget.setLinkDisplay(self)
    
    def mouseDoubleClickEvent(self, _event):
        self.linkRequested()
    
    def contextMenuEvent(self, event):
        return self._linkable_widget.contextMenuEvent(event)

    def setLinkDisplay(self, widget):
        if hasattr(self._linkable_widget, 'setLinkDisplay'):
            self._linkable_widget.setLinkDisplay(widget)
    
    def linkRequested(self):
        if hasattr(self._linkable_widget, 'linkRequested'):
            self._linkable_widget.linkRequested()
