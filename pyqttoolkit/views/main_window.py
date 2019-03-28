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

#pylint: disable=no-name-in-module
from PyQt5.Qt import QMainWindow, QStyleOption, QPainter, QStyle
#pylint: enable=no-name-in-module

from pyqttoolkit.colors import format_color

class MainWindow(QMainWindow):
    def __init__(self, parent, theme_manager):
        QMainWindow.__init__(self, parent)
        self._theme_manager = theme_manager
        self.setStyleSheet(self._get_stylesheet())
    
    def paintEvent(self, _event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
    
    @property
    def themeManager(self):
        return self._theme_manager

    def _get_stylesheet(self):
        color = lambda k: format_color(self._theme_manager.get_color(k))
        color_a = lambda k, a: format_color(self._theme_manager.get_color(k), opacity=a)
        return f"""
QMainWindow, QDialog {{
    background-color: {color('module_background')};
}}

QLabel, QCheckBox, QGroupBox {{
    color: {color('module_text')}
}}
QLabel:disabled, QCheckBox:disabled, QGroupBox:disabled, QPushButton:disabled {{
    color: {color_a('module_text', 0.6)};
}}

QPushButton:disabled {{
background-color:#ccc;
border: 1px solid {color_a('module_text', 0.6)};
}}

QPushButton {{
color: #333;
border: 1px solid #555;
padding: 3px;
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 #888);
}}

QPushButton[class=highlight] {{
color: #333;
border: 1px solid #555;
padding: 3px;
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 {color('highlight')});
}}

QPushButton:hover {{
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
}}

QPushButton:hover[class=highlight] {{
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 {color('highlight_hover')});
}}

QPushButton:pressed {{
background: qradialgradient(cx: 0.4, cy: -0.1, fx: 0.4, fy: -0.1, radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
}}

QPushButton:pressed[class=highlight] {{
background: qradialgradient(cx: 0.4, cy: -0.1, fx: 0.4, fy: -0.1, radius: 1.35, stop: 0 #fff, stop: 1 {color('highlight_pressed')});
}}
"""
