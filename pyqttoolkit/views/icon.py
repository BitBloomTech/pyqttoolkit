#pylint: disable=no-name-in-module
from PyQt5.Qt import QFile, QHBoxLayout, QSize, Qt, QWidget
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtXml import QDomDocument
#pylint: enable=no-name-in-module

from pyqttoolkit.colors import format_color, ColorFormat
from pyqttoolkit.services.theme_manager import ThemeManager
from .styleable import make_styleable

class Icon(QWidget):
    def __init__(self, parent, icon, size=None, padding=None):
        QWidget.__init__(self, parent)
        padding = padding or 0
        self._theme_manager = ThemeManager.get(self)

        self._svgdoc = QDomDocument()
        file = QFile(f'icons:{icon}')
        file.open(QFile.ReadOnly)
        self._svgdoc.setContent(file.readAll())
        file.close()

        self._svgdoc.documentElement().setAttribute('fill', self._get_color())

        self._icon_widget = QSvgWidget(self)
        self._icon_widget.load(self._svgdoc.toByteArray())

        if size:
            self._icon_widget.setFixedSize(QSize(size.width() - 2 * padding, size.height() - 2 * padding))

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.addWidget(self._icon_widget, Qt.AlignCenter)

    def _get_color(self):
        return format_color(self._theme_manager.get_color('button_foreground'), ColorFormat.rgb_string_256)
    
    def setEnabled(self, enabled):
        QWidget.setEnabled(self, enabled)
        self._svgdoc.documentElement().setAttribute('fill', self._get_color())
        self._svgdoc.documentElement().setAttribute('fill-opacity', '1' if self.isEnabled() else '0.4')
        self._icon_widget.load(self._svgdoc.toByteArray())

Icon = make_styleable(Icon)