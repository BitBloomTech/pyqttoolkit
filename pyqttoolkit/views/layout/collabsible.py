#pylint: disable=no-name-in-module
from PyQt5.Qt import QBoxLayout, QToolButton, Qt
#pylint: enable=no-name-in-module

from .lines import HLine, VLine

class CollapsibleLayout(QBoxLayout):
    def __init__(self, parent, direction):
        QBoxLayout.__init__(self, direction, parent)
        self._index = 0
        self._widgets = []
    
    def addWidget(self, widget, group_name, expanded=True):
        QBoxLayout.addWidget(self, self._create_header(group_name, expanded))
        QBoxLayout.addWidget(self, widget)
        self._widgets.append(widget)
        widget.setVisible(expanded)
        self._index += 1
    
    def _create_header(self, name, expanded):
        button = QToolButton(self.parent())
        button.setStyleSheet('QToolButton { border: none; }')
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setArrowType(self._get_arrow(expanded))
        button.setText(name)
        button.setCheckable(True)
        button.setChecked(True)
        button.clicked.connect(self._handle_toggle(button, self._index))
        return button
    
    def _handle_toggle(self, button, index):
        def _handler(checked):
            button.setArrowType(self._get_arrow(checked))
            self._widgets[index].setVisible(checked)
        return _handler

    def _get_arrow(self, expanded):
        return Qt.DownArrow if expanded else Qt.RightArrow

class VCollapsibleLayout(CollapsibleLayout):
    def __init__(self, parent):
        CollapsibleLayout.__init__(self, parent, QBoxLayout.TopToBottom)

class HCollapsibleLayout(CollapsibleLayout):
    def __init__(self, parent):
        CollapsibleLayout.__init__(self, parent, QBoxLayout.LeftToRight)
