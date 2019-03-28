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
