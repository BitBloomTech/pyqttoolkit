# pyqttoolkit
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QBoxLayout, QWidget, QVBoxLayout, QLabel, QSizePolicy

from .lines import HLine, VLine
from .link import LinkWidget

class GroupPanelLayout(QBoxLayout):
    def __init__(self, parent, direction):
        super().__init__(direction, parent)
        self._direction = direction
        self._separator = VLine if not self.isVertical() else HLine
        self._grid_layouts = []
        self._containers = []
        self._separators = []
        self._layouts = []
        self._labels = []
        self._minimum_row_height = 0
        self._spacing = 0
        self._label_alignment = Qt.AlignCenter
        self._panel_direction = QBoxLayout.TopToBottom
        self._group_alignment = None
    
    def addWidget(self, widget, group_name):
        if self._containers:
            self.addSeparator()
        container = LinkWidget(self.parent(), widget)
        layout = QVBoxLayout(container)
        layout.setDirection(self._panel_direction)
        layout.setContentsMargins(self._spacing, self._spacing, self._spacing, self._spacing)
        self.addLabel(container, layout, group_name)
        layout.addWidget(widget)
        group_alignment = self._group_alignment if self._group_alignment is not None else Qt.Alignment(0)
        self._containers.append(container)
        self._layouts.append(layout)
        super().addWidget(container, alignment=group_alignment)

    def setLabelAlignment(self, alignment):
        self._label_alignment = alignment

    def setPanelDirection(self, direction):
        self._panel_direction = direction
    
    def setGroupAlignment(self, alignment):
        self._group_alignment = alignment
    
    def isVertical(self):
        return self._direction in (QBoxLayout.TopToBottom, QBoxLayout.BottomToTop)
    
    def addSeparator(self):
        self._separators.append(self._separator(self.parent()))
        super().addWidget(self._separators[-1])
    
    def addLabel(self, parent, layout, name):
        label = QLabel(name, parent)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label, alignment=self._label_alignment)
        self._labels.append(label)
    
    def addStretch(self, stretch):
        super().addStretch(stretch)

    def setContentsMargins(self, left, top, right, bottom):
        super().setContentsMargins(left, top, right, bottom)
    
    def setSpacing(self, spacing):
        self._spacing = spacing

    def count(self):
        return super().count()
    
    def sizeHint(self):
        return super().sizeHint()
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
    
    def itemAt(self, index):
        return super().itemAt(index)
    
    def takeAt(self, index):
        return super().takeAt(index)
    
    def minimumSize(self):
        return super().minimumSize()
    
    def hasHeightForWidth(self):
        return super().hasHeightForWidth()
    
    def heightForWidth(self, width):
        return super().heightForWidth(width)
    
    def update(self):
        return super().update()

class HGroupPanelLayout(GroupPanelLayout):
    def __init__(self, parent):
        super().__init__(parent, QBoxLayout.LeftToRight)

class VGroupPanelLayout(GroupPanelLayout):
    def __init__(self, parent):
        super().__init__(parent, QBoxLayout.TopToBottom)

class GroupPanelWidget(QWidget):
    def __init__(self, parent, direction):
        super().__init__(parent)
        self._layout = QBoxLayout(direction, self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._direction = direction
        self._separator = VLine if direction == QBoxLayout.LeftToRight else HLine
        self._grid_layouts = []
        self._containers = []
        self._separators = []
        self._layouts = []
        self._labels = []
        self._minimum_row_height = 0
        self._spacing = 0
        self._label_alignment = Qt.AlignCenter
        self._panel_direction = QBoxLayout.TopToBottom
        self._group_alignment = None
    
    def addWidget(self, widget, group_name):
        if self._containers:
            self.addSeparator()
        container = LinkWidget(self, widget)
        layout = QVBoxLayout(container)
        layout.setDirection(self._panel_direction)
        layout.setContentsMargins(self._spacing, self._spacing, self._spacing, self._spacing)
        self.addLabel(container, layout, group_name)
        layout.addWidget(widget)
        group_alignment = self._group_alignment if self._group_alignment is not None else Qt.Alignment(0)
        self._containers.append(container)
        self._layouts.append(layout)
        self._layout.addWidget(container, alignment=group_alignment)

    def setLabelAlignment(self, alignment):
        self._label_alignment = alignment

    def setPanelDirection(self, direction):
        self._panel_direction = direction
    
    def setGroupAlignment(self, alignment):
        self._group_alignment = alignment
    
    def isVertical(self):
        return self._direction in (QBoxLayout.TopToBottom, QBoxLayout.BottomToTop)
    
    def addSeparator(self):
        self._separators.append(self._separator(self))
        self._layout.addWidget(self._separators[-1])
    
    def addLabel(self, parent, layout, name):
        label = QLabel(name, parent)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label, alignment=self._label_alignment)
        self._labels.append(label)
    
    def addStretch(self, stretch):
        self._layout.addStretch(stretch)

    def setContentsMargins(self, left, top, right, bottom):
        self._layout.setContentsMargins(left, top, right, bottom)
    
    def setSpacing(self, spacing):
        self._spacing = spacing

class HGroupPanelWidget(GroupPanelWidget):
    def __init__(self, parent):
        super().__init__(parent, QBoxLayout.LeftToRight)

class VGroupPanelWidget(GroupPanelWidget):
    def __init__(self, parent):
        super().__init__(parent, QBoxLayout.TopToBottom)
