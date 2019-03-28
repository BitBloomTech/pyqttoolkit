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
from PyQt5.Qt import QWidget, pyqtSignal, QGridLayout, QLabel, QColor, QPalette
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty, bind
from pyqttoolkit.views import BindableCheckBox, BindableLineEdit
from pyqttoolkit.colors import format_color, ColorFormat

class LegendControlView(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._series = None
        self._handles = None
        self._show_series = []
        self._series_names = []

        self._layout = QGridLayout(self)

        self._show_legend = BindableCheckBox(None, self)
        
        self._layout.addWidget(self._show_legend, 0, 0)
        self._layout.addWidget(QLabel(self.tr('Show Legend')), 0, 1)

        self.showLegend = False
        bind(self, self._show_legend, 'showLegend', 'checked')
        self.hasHiddenSeries = False
            
    showLegendChanged = pyqtSignal(bool)
    showSeriesChanged = pyqtSignal(int, bool)
    seriesNameChanged = pyqtSignal(int, str)
    hasHiddenSeriesChanged = pyqtSignal(bool)
    seriesUpdated = pyqtSignal()

    showLegend = AutoProperty(bool)
    hasHiddenSeries = AutoProperty(bool)

    def setSeries(self, series, handles, colors):
        if self._series == series and self._handles == handles:
            return

        self._series = series
        self._handles = handles

        for widget in self._show_series + self._series_names:
            self._layout.removeWidget(widget)
            widget.setParent(None)
        
        self._show_series = []
        self._series_names = []

        for i, default_name in enumerate(series):
            show_series = BindableCheckBox(None, self)
            show_series.setStyleSheet(self._check_box_style_sheet(colors[i]))
            show_series.checked = True
            show_series.checkedChanged.connect(self._on_show_series_changed(i))
            series_name = BindableLineEdit(self)
            series_name.setPlaceholderText(default_name)
            series_name.valueChanged.connect(self._on_series_name_changed(i))
            self._show_series.append(show_series)
            self._series_names.append(series_name)
            self._layout.addWidget(show_series, i + 1, 0)
            self._layout.addWidget(series_name, i + 1, 1)
        
        self.seriesUpdated.emit()
    
    def _check_box_style_sheet(self, color):
        color = color or (255, 255, 255)
        return """BindableCheckBox::indicator:checked
            {{
                background-color: {color}
            }}
            BindableCheckBox::indicator:unchecked
            {{
                border: 3px solid {color}
            }}
        """.format(color=format_color(color, ColorFormat.hexa_string, 1.0))

    @property
    def seriesNames(self):
        return [sn.value or sn.placeholderText() for sn in self._series_names]

    @property
    def showSeries(self):
        return [ss.checked for ss in self._show_series]
    
    @property
    def seriesHandles(self):
        return self._handles

    def _on_show_series_changed(self, index):
        def _(show):
            self.showSeriesChanged.emit(index, show)
            self.hasHiddenSeries = not all(self.showSeries)
        return _
    
    def _on_series_name_changed(self, index):
        def _():
            self.seriesNameChanged.emit(index, self._series_names[index].value or self._series_names[index].placeholderText())
        return _