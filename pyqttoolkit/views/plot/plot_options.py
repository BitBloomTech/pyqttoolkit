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
import numpy as np

#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget, pyqtSignal, QGridLayout, QLabel
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty, bind
from pyqttoolkit.views import BindableCheckBox, AutoFloatLineEdit

class PlotOptionsView(QWidget):
    def __init__(self, parent, grid_lines=True, x_limits=True, y_limits=True, secondary_x_limits=False, secondary_y_limits=False):
        QWidget.__init__(self, parent)

        edit_width = 60
        self._grid_lines = grid_lines
        self._x_limits = x_limits
        self._y_limits = y_limits
        self._secondary_y_limits = secondary_y_limits
        self._secondary_x_limits = secondary_x_limits

        self.showGridLines = False
        self.xAxisLowerLimit = self.xAxisUpperLimit = self.yAxisLowerLimit = self.yAxisUpperLimit = float('nan')
        self.secondaryXAxisLowerLimit = self.secondaryXAxisUpperLimit = self.secondaryYAxisLowerLimit = self.secondaryYAxisUpperLimit = float('nan')

        self._layout = QGridLayout(self)
        if grid_lines:
            self._show_gridlines = BindableCheckBox(None, self)
            self._layout.addWidget(QLabel(self.tr('Show Grid Lines'), self), 0, 0)
            self._layout.addWidget(self._show_gridlines, 0, 1)
            bind(self, self._show_gridlines, 'showGridLines', 'checked')
        else:
            self._show_gridlines = None

        if x_limits:
            self._x_axis_lower_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._x_axis_upper_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._x_axis_lower_limit.setFixedWidth(edit_width)
            self._x_axis_upper_limit.setFixedWidth(edit_width)
            self._layout.addWidget(QLabel(self.tr('X Axis Limits'), self), 1, 0)
            self._layout.addWidget(self._x_axis_lower_limit, 1, 1)
            self._layout.addWidget(self._x_axis_upper_limit, 1, 2)
            bind(self, self._x_axis_lower_limit, 'xAxisLowerLimit', 'value')
            bind(self, self._x_axis_upper_limit, 'xAxisUpperLimit', 'value')
        else:
            self._x_axis_lower_limit = self._x_axis_upper_limit = None

        if y_limits:
            self._y_axis_lower_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._y_axis_upper_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._y_axis_lower_limit.setFixedWidth(edit_width)
            self._y_axis_upper_limit.setFixedWidth(edit_width)
            self._layout.addWidget(QLabel(self.tr('Y Axis Limits'), self), 2, 0)
            self._layout.addWidget(self._y_axis_lower_limit, 2, 1)
            self._layout.addWidget(self._y_axis_upper_limit, 2, 2)
            bind(self, self._y_axis_lower_limit, 'yAxisLowerLimit', 'value')
            bind(self, self._y_axis_upper_limit, 'yAxisUpperLimit', 'value')
        else:
            self._y_axis_lower_limit = self._y_axis_upper_limit = None
        
        if secondary_y_limits:
            self._secondary_y_axis_lower_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._secondary_y_axis_upper_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._secondary_y_axis_lower_limit.setFixedWidth(edit_width)
            self._secondary_y_axis_upper_limit.setFixedWidth(edit_width)
            self._secondary_y_limits_label = QLabel(self.tr('2nd Y Axis Limits'), self)
            self._layout.addWidget(self._secondary_y_limits_label, 3, 0)
            self._layout.addWidget(self._secondary_y_axis_lower_limit, 3, 1)
            self._layout.addWidget(self._secondary_y_axis_upper_limit, 3, 2)
            bind(self, self._secondary_y_axis_lower_limit, 'secondaryYAxisLowerLimit', 'value')
            bind(self, self._secondary_y_axis_upper_limit, 'secondaryYAxisUpperLimit', 'value')
        else:
            self._secondary_y_axis_lower_limit = self._secondary_y_axis_upper_limit = self._secondary_y_limits_label = None

        if secondary_x_limits:
            self._secondary_x_axis_lower_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._secondary_x_axis_upper_limit = AutoFloatLineEdit(self, allow_inf=False, formatter=self._value_formatter)
            self._secondary_x_axis_lower_limit.setFixedWidth(edit_width)
            self._secondary_x_axis_upper_limit.setFixedWidth(edit_width)
            self._secondary_x_limits_label = QLabel(self.tr('2nd X Axis Limits'), self)
            self._layout.addWidget(self._secondary_x_limits_label, 4, 0)
            self._layout.addWidget(self._secondary_x_axis_lower_limit, 4, 1)
            self._layout.addWidget(self._secondary_x_axis_upper_limit, 4, 2)
            bind(self, self._secondary_x_axis_lower_limit, 'secondaryXAxisLowerLimit', 'value')
            bind(self, self._secondary_x_axis_upper_limit, 'secondaryXAxisUpperLimit', 'value')
        else:
            self._secondary_x_axis_lower_limit = self._secondary_x_axis_upper_limit = self._secondary_x_limits_label = None


    showGridLinesChanged = pyqtSignal(bool)
    xAxisLowerLimitChanged = pyqtSignal(float)
    xAxisUpperLimitChanged = pyqtSignal(float)
    xAxisLimitsChanged = pyqtSignal(float, float)
    yAxisLowerLimitChanged = pyqtSignal(float)
    yAxisUpperLimitChanged = pyqtSignal(float)
    yAxisLimitsChanged = pyqtSignal(float, float)
    secondaryXAxisLowerLimitChanged = pyqtSignal(float)
    secondaryXAxisUpperLimitChanged = pyqtSignal(float)
    secondaryXAxisLimitsChanged = pyqtSignal(float, float)
    secondaryYAxisLowerLimitChanged = pyqtSignal(float)
    secondaryYAxisUpperLimitChanged = pyqtSignal(float)
    secondaryYAxisLimitsChanged = pyqtSignal(float, float)

    showGridLines = AutoProperty(bool)
    xAxisLowerLimit = AutoProperty(float)
    xAxisUpperLimit = AutoProperty(float)
    yAxisLowerLimit = AutoProperty(float)
    yAxisUpperLimit = AutoProperty(float)
    secondaryYAxisLowerLimit = AutoProperty(float)
    secondaryYAxisUpperLimit = AutoProperty(float)
    secondaryXAxisLowerLimit = AutoProperty(float)
    secondaryXAxisUpperLimit = AutoProperty(float)

    def _value_formatter(self, value):
        if isinstance(value, str):
            return value
        if value == np.inf:
            return 'inf'
        if value == -np.inf:
            return '-inf'
        if np.isnan(value):
            return 'Auto'
        value = int(value * 100) / 100
        return '{0:.2g}'.format(value)
    
    @property
    def grid_lines(self):
        return self._grid_lines
    
    def setXLimits(self, x_lower, x_upper):
        blocked = self.blockSignals(True)
        self.xAxisLowerLimit = x_lower
        self._x_axis_lower_limit.value = x_lower
        self.xAxisUpperLimit = x_upper
        self._x_axis_upper_limit.value = x_upper
        self.blockSignals(blocked)
        self.xAxisLimitsChanged.emit(x_lower, x_upper)
    
    def setYLimits(self, y_lower, y_upper):
        blocked = self.blockSignals(True)
        self.yAxisLowerLimit = y_lower
        self._y_axis_lower_limit.value = y_lower
        self.yAxisUpperLimit = y_upper
        self._y_axis_upper_limit.value = y_upper
        self.blockSignals(blocked)
        self.yAxisLimitsChanged.emit(y_lower, y_upper)
    
    def setSecondaryXLimits(self, x_lower, x_upper):
        blocked = self.blockSignals(True)
        self.secondaryXAxisLowerLimit = x_lower
        self._secondary_x_axis_lower_limit.value = x_lower
        self.secondaryXAxisUpperLimit = x_upper
        self._secondary_x_axis_upper_limit.value = x_upper
        self.blockSignals(blocked)
        self.secondaryXAxisLimitsChanged.emit(x_lower, x_upper)
    
    def setSecondaryYLimits(self, y_lower, y_upper):
        blocked = self.blockSignals(True)
        self.secondaryYAxisLowerLimit = y_lower
        self._secondary_y_axis_lower_limit.value = y_lower
        self.secondaryYAxisUpperLimit = y_upper
        self._secondary_y_axis_upper_limit.value = y_upper
        self.blockSignals(blocked)
        self.secondaryYAxisLimitsChanged.emit(y_lower, y_upper)
    
    @property
    def x_limits(self):
        return self._x_limits
    
    @property
    def y_limits(self):
        return self._y_limits

    @property
    def secondary_y_limits(self):
        return self._secondary_y_limits

    @property
    def secondary_x_limits(self):
        return self._secondary_x_limits

    def setSecondaryYLimitsEnabled(self, enabled):
        if self._secondary_y_limits:
            self._secondary_y_axis_lower_limit.setEnabled(enabled)
            self._secondary_y_axis_upper_limit.setEnabled(enabled)
            self._secondary_y_limits_label.setEnabled(enabled)

    def setSecondaryXLimitsEnabled(self, enabled):
        if self._secondary_x_limits:
            self._secondary_x_axis_lower_limit.setEnabled(enabled)
            self._secondary_x_axis_upper_limit.setEnabled(enabled)
            self._secondary_x_limits_label.setEnabled(enabled)
