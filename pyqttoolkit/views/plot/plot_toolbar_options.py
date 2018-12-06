#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget, QGridLayout, Qt, QSizePolicy, QVBoxLayout
#pylint: enable=no-name-in-module

from pyqttoolkit.views import PopoutWidget, make_styleable
from pyqttoolkit.colors import interpolate_rgb, format_color, ColorFormat
from pyqttoolkit.views.layout import HLine

from .tool_type import ToolType
from .toolbar import PlotToolbarWidget
from .plot_options import PlotOptionsView

def _to_qt_color(color):
    return tuple(c * 255 for c in color)

class ToolbarContainer(QWidget):
    pass

ToolbarContainer = make_styleable(ToolbarContainer)

class PlotToolbarOptions(QWidget):
    def __init__(self, parent, series_style, plot, options=None, right_padding=0.0, has_extra_tools=False):
        QWidget.__init__(self, parent)
        self._plot = plot
        self._toolbar_container = ToolbarContainer(plot)
        
        self._background_color_qt = _to_qt_color(series_style.get_color_from_key('axes_background'))
        self._foreground_color_qt = _to_qt_color(series_style.get_color_from_key('axes_foreground'))
        interpolation = interpolate_rgb(self._background_color_qt, self._foreground_color_qt, 3)
        self._icon_hover_color = interpolation[1]

        self._toolbar = PlotToolbarWidget(self._toolbar_container, plot, self._foreground_color_qt, self._icon_hover_color)
        self._toolbar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(plot, 0, 0, 1, 3)
        self._background_opacity = 0.8
        plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if options is not None:
            if isinstance(options, PlotOptionsView):
                plot.setOptionsView(options)
            self._options = PopoutWidget(self, options, self._background_color_qt, self._foreground_color_qt, self._background_opacity)
            self._options.setVisible(False)
            self._layout.addWidget(self._options, 0, 0, Qt.AlignRight)
            self._toolbar.toolActivated.connect(self._handle_tool_activated)
        else:
            self._options = None
        
        self._toolbar_layout = QVBoxLayout(self._toolbar_container)
        self._toolbar_layout.addWidget(self._toolbar, Qt.AlignTop)

        self._layout.addWidget(self._toolbar_container, 0, 1, Qt.AlignRight | Qt.AlignTop)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 0)
        if right_padding > 0:
            self._padding_widget = QWidget(self)
            self._padding_widget.setVisible(False)
            self._layout.addWidget(self._padding_widget, 0, 2)
            self._layout.setColumnMinimumWidth(2, right_padding)
        else:
            self._padding_widget = None
        
        if not has_extra_tools:
            self._toolbar_layout.addStretch()

    def _handle_tool_activated(self, tool, active):
        if tool == ToolType.options:
            self._options.setVisible(active)
            if self._padding_widget:
                self._padding_widget.setVisible(active)
            if active:
                self._toolbar_container.setStyleSheet("ToolbarContainer {{ background-color: {} }}".format(format_color(self._background_color_qt, ColorFormat.rgba_string_256, self._background_opacity)))
                self._layout.setAlignment(self._toolbar_container, Qt.AlignRight)
                if self._padding_widget:
                    self._padding_widget.setStyleSheet("QWidget {{ background-color: {} }}".format(format_color(self._background_color_qt, ColorFormat.rgba_string_256, self._background_opacity)))
            else:
                self._layout.setAlignment(self._toolbar_container, Qt.AlignRight | Qt.AlignTop)
                self._toolbar_container.setStyleSheet("")
                if self._padding_widget:
                    self._padding_widget.setStyleSheet("")

    def addTool(self, tool_widget):
        self._toolbar_layout.addWidget(HLine(self._plot), Qt.AlignTop)
        self._toolbar_layout.addWidget(tool_widget, Qt.AlignTop | Qt.AlignCenter)
        self._toolbar_layout.addStretch()
    
    @property
    def icon_color(self):
        return self._foreground_color_qt

    @property
    def icon_hover_color(self):
        return self._icon_hover_color

    @property
    def toolbar(self):
        return self._toolbar
