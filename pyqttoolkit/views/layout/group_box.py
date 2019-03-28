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
from PyQt5.Qt import QGroupBox, QGridLayout, Qt, QVBoxLayout
#pylint: enable=no-name-in-module

class LinkGroupBox(QGroupBox):
    def __init__(self, name, parent, linkable_widget):
        QGroupBox.__init__(self, name, parent)
        self._linkable_widget = linkable_widget
        if hasattr(self._linkable_widget, 'setLinkDisplay'):
            self._linkable_widget.setLinkDisplay(self)
    
    def mouseDoubleClickEvent(self, _event):
        if hasattr(self._linkable_widget, 'linkRequested'):
            self._linkable_widget.linkRequested()

def wrap_in_group_box(widget, parent, name, alignment=Qt.AlignTop):
    group_box = LinkGroupBox(name, parent, widget)
    group_box_layout = QGridLayout(group_box)
    if alignment is not None:
        group_box_layout.addWidget(widget, 0, 0, alignment)
    else:
        group_box_layout.addWidget(widget, 0, 0)
    return group_box

def wrap_many_in_group_box(widgets, parent, name, alignment=Qt.AlignTop):
    group_box = QGroupBox(name, parent)
    group_box_layout = QVBoxLayout(group_box)
    for widget in widgets:
        if alignment is not None:
            group_box_layout.addWidget(widget, alignment)
        else:
            group_box_layout.addWidget(widget)
    return group_box
