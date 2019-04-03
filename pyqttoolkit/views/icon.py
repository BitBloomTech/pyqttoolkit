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
from PyQt5.Qt import QFile, QHBoxLayout, QSize, Qt, QWidget
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtXml import QDomDocument
#pylint: enable=no-name-in-module

from pyqttoolkit.colors import format_color, ColorFormat
from pyqttoolkit.services.theme_manager import ThemeManager
from .styleable import make_styleable

class Icon(QWidget):
    def __init__(self, parent, icon, size=None, padding=None, color=None):
        QWidget.__init__(self, parent)
        padding = padding or 0
        self._theme_manager = ThemeManager.get(self)
        
        self._color = format_color(color or self._theme_manager.get_color('button_foreground'), ColorFormat.rgb_string_256)

        self._svgdoc = QDomDocument()
        self._icon_widget = QSvgWidget(self)

        self.loadIcon(icon)

        if size:
            self._icon_widget.setFixedSize(QSize(size.width() - 2 * padding, size.height() - 2 * padding))

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.addWidget(self._icon_widget, Qt.AlignCenter)
    
    def loadIcon(self, icon):
        file = QFile(f'icons:{icon}')
        file.open(QFile.ReadOnly)
        self._svgdoc.setContent(file.readAll())
        self._svgdoc.documentElement().setAttribute('fill', self._color)
        file.close()
        self._icon_widget.load(self._svgdoc.toByteArray())

    def setEnabled(self, enabled):
        QWidget.setEnabled(self, enabled)
        self._svgdoc.documentElement().setAttribute('fill', self._color)
        self._svgdoc.documentElement().setAttribute('fill-opacity', '1' if self.isEnabled() else '0.4')
        self._icon_widget.load(self._svgdoc.toByteArray())
    
    def setColor(self, color=None):
        color = format_color(color or self._theme_manager.get_color('button_foreground'), ColorFormat.rgb_string_256) or self._color
        self._svgdoc.documentElement().setAttribute('fill', color)
        self._svgdoc.documentElement().setAttribute('fill-opacity', '1' if self.isEnabled() else '0.4')
        self._icon_widget.load(self._svgdoc.toByteArray())

Icon = make_styleable(Icon)
