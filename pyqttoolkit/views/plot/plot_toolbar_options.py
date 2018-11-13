#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget, QGridLayout, Qt
#pylint: enable=no-name-in-module

from pyqttoolkit.views import PopoutWidget

from .tool_type import ToolType
from .toolbar import PlotToolbarWidget

def _to_qt_color(color):
    return tuple(c * 255 for c in color)

class PlotToolbarOptions(QWidget):
    def __init__(self, parent, series_style, plot, options=None):
        QWidget.__init__(self, parent)
        self._toolbar = PlotToolbarWidget(self, plot)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(plot, 0, 0)
        if options is not None:
            self._options = PopoutWidget(self, options, _to_qt_color(series_style.get_color_from_key('axes_background')), _to_qt_color(series_style.get_color_from_key('axes_foreground')))
            self._options.setVisible(False)
            self._layout.addWidget(self._options, 0, 0, Qt.AlignRight)
            self._toolbar.toolActivated.connect(self._handle_tool_activated)
        else:
            self._options = None
        self._layout.addWidget(self._toolbar, 0, 1)

    def _handle_tool_activated(self, tool, active):
        if tool == ToolType.options:
            self._options.setVisible(active)
