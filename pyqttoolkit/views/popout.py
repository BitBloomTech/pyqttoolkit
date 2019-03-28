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
from PyQt5.Qt import QWidget, QVBoxLayout, Qt, QSizePolicy, QGridLayout
#pylint: enable=no-name-in-module

from pyqttoolkit.views.styleable import make_styleable
from pyqttoolkit.colors import format_color

class PopoutWidget(QWidget):
    def __init__(self, parent, content, background_color, foreground_color, background_opacity=0.8):
        QWidget.__init__(self, parent)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(content, 0, 0, Qt.AlignTop)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        stylesheet = """
PopoutWidget {{
    background-color: {background_color}
}}

QLabel {{
    color: {foreground_color}
}}"""

        self.setStyleSheet(stylesheet.format(background_color=format_color(background_color, opacity=background_opacity), foreground_color=format_color(foreground_color)))

PopoutWidget = make_styleable(PopoutWidget)