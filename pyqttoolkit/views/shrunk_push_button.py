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
from PyQt5.Qt import QSize
from PyQt5.QtWidgets import QPushButton
#pylint: enable=no-name-in-module

from .styleable import make_styleable

class ShrunkPushButton(QPushButton):
    def __init__(self, text, parent):
        QPushButton.__init__(self, text, parent)

    def sizeHint(self):
        return QSize(self.fontMetrics().width(self.text()) + 10, QPushButton.sizeHint(self).height())

ShrunkPushButton = make_styleable(ShrunkPushButton)

class VShrunkPushButton(ShrunkPushButton):
    def __init__(self, text, parent):
        super(VShrunkPushButton, self).__init__(self, text, parent)
        self.setFixedHeight(22)
