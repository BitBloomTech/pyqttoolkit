#pylint: disable=no-name-in-module
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