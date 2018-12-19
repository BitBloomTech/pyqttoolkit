#pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt
from PyQt5.Qt import QLayout, QBoxLayout, QWidget, QVBoxLayout, QLabel, QSizePolicy
#pylint: enable=no-name-in-module

from .lines import HLine, VLine

class LinkWidget(QWidget):
    def __init__(self, parent, linkable_widget):
        QWidget.__init__(self, parent)
        self._linkable_widget = linkable_widget
        if hasattr(self._linkable_widget, 'setLinkDisplay'):
            self._linkable_widget.setLinkDisplay(self)
    
    def mouseDoubleClickEvent(self, _event):
        if hasattr(self._linkable_widget, 'linkRequested'):
            self._linkable_widget.linkRequested()

class GroupPanelLayout(QLayout):
    def __init__(self, parent, direction):
        QLayout.__init__(self, parent)
        self._inner = QBoxLayout(direction)
        self._direction = direction
        self._separator = VLine if not self.isVertical() else HLine
        self._item_count = 0
        self._grid_layouts = []
        self._minimum_row_height = 0
        self._spacing = 0
        self._label_alignment = Qt.AlignCenter
        self._panel_direction = QBoxLayout.TopToBottom
        self._group_alignment = None
    
    def addWidget(self, widget, group_name):
        if self._item_count > 0:
            self.addSeparator()
        container = LinkWidget(self.parent(), widget)
        layout = QVBoxLayout(container)
        layout.setDirection(self._panel_direction)
        layout.setContentsMargins(self._spacing, self._spacing, self._spacing, self._spacing)
        self.addLabel(layout, group_name)
        layout.addWidget(widget)
        container.setLayout(layout)
        group_alignment = self._group_alignment if self._group_alignment is not None else Qt.Alignment(0)
        self._inner.addWidget(container, alignment=group_alignment)
        self._item_count += 1

    def setLabelAlignment(self, alignment):
        self._label_alignment = alignment

    def setPanelDirection(self, direction):
        self._panel_direction = direction
    
    def setGroupAlignment(self, alignment):
        self._group_alignment = alignment
    
    def isVertical(self):
        return self._direction in (QBoxLayout.TopToBottom, QBoxLayout.BottomToTop)
    
    def addSeparator(self):
        self._inner.addWidget(self._separator(self.parent()))
    
    def addLabel(self, layout, name):
        label = QLabel(name)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label, alignment=self._label_alignment)
    
    def addStretch(self, stretch):
        self._inner.addStretch(stretch)

    def setContentsMargins(self, left, top, right, bottom):
        self._inner.setContentsMargins(left, top, right, bottom)
    
    def setSpacing(self, spacing):
        self._spacing = spacing

    def count(self):
        return self._inner.count()
    
    def sizeHint(self):
        return self._inner.sizeHint()
    
    def setGeometry(self, rect):
        self._inner.setGeometry(rect)
    
    def itemAt(self, index):
        return self._inner.itemAt(index)
    
    def takeAt(self, index):
        return self._inner.takeAt(index)
    
    def minimumSize(self):
        return self._inner.minimumSize()
    
    def hasHeightForWidth(self):
        return self._inner.hasHeightForWidth()
    
    def heightForWidth(self, width):
        return self._inner.heightForWidth(width)
    
    def update(self):
        return self._inner.update()

class HGroupPanelLayout(GroupPanelLayout):
    def __init__(self, parent):
        GroupPanelLayout.__init__(self, parent, QBoxLayout.LeftToRight)

class VGroupPanelLayout(GroupPanelLayout):
    def __init__(self, parent):
        GroupPanelLayout.__init__(self, parent, QBoxLayout.TopToBottom)
