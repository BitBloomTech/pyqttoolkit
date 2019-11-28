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
from PyQt5.Qt import QFrame, QPoint, Qt, QGridLayout, QRect
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
        if isinstance(rect, QRect):
            new_pos = parent.mapToGlobal(rect.bottomRight() - QPoint(self.width(), 0))
            new_pos = QPoint(max(0, new_pos.x()), new_pos.y())
        elif isinstance(rect, QPoint):
            new_pos = parent.mapToGlobal(rect)
        self.move(new_pos)

    @property
    def contents(self):
        return self._contents