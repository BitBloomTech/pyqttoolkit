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
from PyQt5.Qt import QWidget, QGridLayout, Qt, QSizePolicy, QVBoxLayout
#pylint: enable=no-name-in-module

from pyqttoolkit.views import PopoutWidget, make_styleable
from pyqttoolkit.colors import interpolate_rgb, format_color, ColorFormat
from pyqttoolkit.views.layout import HLine

from .tool_type import ToolType
from .toolbar import PlotToolbarWidget
from .plot_options import PlotOptionsView
from .legend_control import LegendControlView

def _to_qt_color(color):
    return tuple(c * 255 for c in color)

class ToolbarContainer(QWidget):
    pass

ToolbarContainer = make_styleable(ToolbarContainer)

class PlotToolbarOptions(QWidget):
    def __init__(self, parent, series_style, theme_manager, plot, options=None, legend_control=None, right_padding=0.0, has_extra_tools=False):
        QWidget.__init__(self, parent)
        self._theme_manager = theme_manager
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
            self._options = self._add_popout(ToolType.options, options)
        else:
            self._options = None

        if legend_control is not None:
            if isinstance(legend_control, LegendControlView):
                plot.setLegendControl(legend_control)
            self._legend_control = self._add_popout(ToolType.legend, legend_control)
            legend_control.hasHiddenSeriesChanged.connect(self._handle_has_hidden_series_changed)
        else:
            self._legend_control = None
        
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
    
    def _handle_has_hidden_series_changed(self, has_hidden):
        color = None if not has_hidden else self._theme_manager.get_color('highlight')
        self._toolbar.setColor(ToolType.legend, color)

    def _handle_tool_activated(self, tool_type, view):
        def _(tool, active):
            if tool == tool_type:
                view.setVisible(active)
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
        return _

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

    def _add_popout(self, tool_type, view):
        popout = PopoutWidget(self, view, self._background_color_qt, self._foreground_color_qt, self._background_opacity)
        popout.setVisible(False)
        self._layout.addWidget(popout, 0, 0, Qt.AlignRight)
        self._toolbar.toolActivated.connect(self._handle_tool_activated(tool_type, popout))
        return popout