
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
QLabel:disabled, QCheckBox:disabled, QGroupBox:disabled {{
    color: {color_a('module_text', 0.6)};
}}
"""
