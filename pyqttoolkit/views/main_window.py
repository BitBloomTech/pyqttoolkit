
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
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 #ff609a);
}}

QPushButton:hover {{
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
}}

QPushButton:hover[class=highlight] {{
background: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4, radius: 1.35, stop: 0 #fff, stop: 1 #ffa3c4);
}}

QPushButton:pressed {{
background: qradialgradient(cx: 0.4, cy: -0.1, fx: 0.4, fy: -0.1, radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
}}

QPushButton:pressed[class=highlight] {{
background: qradialgradient(cx: 0.4, cy: -0.1, fx: 0.4, fy: -0.1, radius: 1.35, stop: 0 #fff, stop: 1 #ff93ba);
}}
"""
