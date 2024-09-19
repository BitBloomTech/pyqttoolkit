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
from io import BytesIO
import numpy as np
from datetime import datetime

from PyQt5.QtCore import pyqtSignal, QSize, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMenu, QAction, QApplication
from PyQt5.QtGui import QKeySequence, QImage

import matplotlib
from matplotlib.legend import DraggableLegend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector, SpanSelector
from mpl_toolkits.axes_grid1 import Size, Divider
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from matplotlib.projections.polar import PolarAxes

import pandas as pd

from pyqttoolkit.properties import AutoProperty, connect_all, bind
from pyqttoolkit.models import SpanModel
from pyqttoolkit.views import TableView
from pyqttoolkit.colors import interpolate_rgb
from contextlib import contextmanager

from ..tool_type import ToolType
from .font import MatPlotLibFont

def _to_finite(value):
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if value is None:
        value = np.nan
    return value if isinstance(value, datetime) or np.isfinite(value) else 0

def _safe_limits(lower, upper):
    lower = _to_finite(lower)
    upper = _to_finite(upper)
    return min(lower, upper), max(lower, upper)

def _cartesian_polar_selector(base_class):
    class _CartesianPolarSelector(base_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._polar_projection = isinstance(self.ax, PolarAxes)
        
        def _get_data(self, event):
            if self._polar_projection:
                xdata = event.xdata + 2 * np.pi if event.xdata < 0 else event.xdata
                ydata = np.clip(event.ydata, *self.ax.get_ybound())
                return xdata, ydata
            else:
                return super()._get_data(event)
    
    return _CartesianPolarSelector

class _SpanSelector(_cartesian_polar_selector(SpanSelector)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._select_none_handler = None
        self._min_span = 1.0

    @property
    def rect(self):
        return self._selection_artist

    @property
    def handles(self):
        return self._edge_handles

    def _release(self, event):
        SpanSelector._release(self, event)
        if self.rect.get_width() < self._min_span:
            self.rect.set_visible(False)
            if self._select_none_handler is not None:
                self._select_none_handler()
    
    def set_on_select_none(self, handler):
        self._select_none_handler = handler
    
    def set_min_span(self, min_span):
        self._min_span = min_span

class _RectangleSelector(_cartesian_polar_selector(RectangleSelector)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _press(self, event):
        if not self._interactive:
            x = event.xdata
            y = event.ydata
            self.extents = x, x, y, y
        RectangleSelector._press(self, event)

class MatPlotLibBase(QWidget):
    def __init__(self,
        parent, file_dialog_service,
        h_margin=(0.8, 0.1), v_margin=(0.5, 0.15),
        h_axes=None, v_axes=None,
        nx_default=1, ny_default=1
        ):
        QWidget.__init__(self, parent)
        self._file_dialog_service = file_dialog_service
        self._figure = Figure()
        self._canvas = FigureCanvas(self._figure)
        h = [Size.Fixed(h_margin[0]), *(h_axes or [Size.Scaled(1.0)]), Size.Fixed(h_margin[1])]
        v = [Size.Fixed(v_margin[0]), *(v_axes or [Size.Scaled(1.0)]), Size.Fixed(v_margin[1])]
        self._divider = Divider(self._figure, (0.0, 0.0, 1.0, 1.0), h, v, aspect=False)
        self._axes = Axes(self._figure, self._divider.get_position())
        self._axes.set_axes_locator(self._divider.new_locator(nx=nx_default, ny=ny_default))
        self._axes.set_zorder(2)
        self._axes.patch.set_visible(False)
        for spine in ['top', 'right']:
            self._axes.spines[spine].set_visible(False)
        self._figure.add_axes(self._axes)

        self._canvas.setParent(self)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._canvas)
        self.setLayout(self._layout)

        self._figure.canvas.mpl_connect('scroll_event', self._on_scroll)
        self._xy_extents = None
        self._background_cache = None
        self._decoration_artists = []
        self._is_panning = False
        
        self._zoom_selector = _RectangleSelector(self._axes, self._zoom_selected, interactive=True)
        self._zoom_selector.set_active(False)
        self._x_extent_padding = 0.01
        self._y_extent_padding = 0.01
        self._axes.ticklabel_format(style='sci', axis='x', scilimits=(-4, 4))
        self._axes.ticklabel_format(style='sci', axis='y', scilimits=(-4, 4))
        self._active_tools = {}
        self._span = _SpanSelector(
            self._axes, self._handle_span_select, 'horizontal',
            props=dict(alpha=0.2, facecolor='red', edgecolor='k'),
            interactive=True, drag_from_anywhere=True, handle_props=dict(alpha=0.0),
            ignore_event_outside=True
        )
        self._span.set_on_select_none(self._handle_span_select_none)
        self.span = self._previous_span = None
        self._span_center_mouse_event = None
        self._span_left_mouse_event = None
        self._span_right_mouse_event = None
        self._figure.canvas.mpl_connect('button_press_event', self._handle_press)
        self._figure.canvas.mpl_connect('motion_notify_event', self._handle_move)
        self._figure.canvas.mpl_connect('button_release_event', self._handle_release)
        self._figure.canvas.mpl_connect('resize_event', self._handle_resize)
        self.activateTool(ToolType.span, self.isActiveDefault(ToolType.span))
        self._pan_event = None
        self._pending_draw = None
        self._pending_artists_draw = None
        self._other_draw_events = []
        self._draw_timer = QTimer(self)
        self._draw_timer.timeout.connect(self._do_draw_events)
        self._draw_timer.start(20)
        self._zoom_skew = None

        self._menu = QMenu(self)
        self._copy_image_action = QAction(self.tr('Copy To Clipboard'), self)
        self._copy_image_action.triggered.connect(self.copyToClipboard)
        self._copy_image_action.setShortcuts(QKeySequence.Copy)
        self._save_image_action = QAction(self.tr('Save As Image'), self)
        self._save_image_action.triggered.connect(self.saveAsImage)
        self._show_table_action = QAction(self.tr('Show Table'), self)
        self._show_table_action.triggered.connect(self.showTable)
        self._menu.addAction(self._copy_image_action)
        self._menu.addAction(self._save_image_action)
        self._menu.addAction(self._show_table_action)
        self.addAction(self._copy_image_action)

        self._table_view = None
        self._single_axis_zoom_enabled = True
        self._cached_label_width_height = None

        if hasattr(type(self), 'dataChanged'):
            self.dataChanged.connect(self._on_data_changed)
        
        self._options_view = None
        self._secondary_axes = self._secondary_y_extent = self._secondary_x_extent = None
        self._legend = None
        self._draggable_legend = None
        self._setting_axis_limits = False

        self.hasHiddenSeries = False

    enabledToolsChanged = pyqtSignal()
    spanChanged = pyqtSignal(SpanModel)
    hasHiddenSeriesChanged = pyqtSignal(bool)
    yTickLabelsWidthAdjusted = pyqtSignal()

    span = AutoProperty(SpanModel)
    hasHiddenSeries = AutoProperty(bool)

    @property
    def divider(self):
        return self._divider

    def setOptionsView(self, options_view):
        self._options_view = options_view
        self._options_view.setSecondaryYLimitsEnabled(self._secondary_y_enabled())
        self._options_view.setSecondaryXLimitsEnabled(self._secondary_x_enabled())

        self._options_view.showGridLinesChanged.connect(self._update_grid_lines)
        self._options_view.xAxisLowerLimitChanged.connect(self._handle_options_view_limit_changed(x_min_changed=True))
        self._options_view.xAxisUpperLimitChanged.connect(self._handle_options_view_limit_changed(x_max_changed=True))
        self._options_view.yAxisLowerLimitChanged.connect(self._handle_options_view_limit_changed(y_min_changed=True))
        self._options_view.yAxisUpperLimitChanged.connect(self._handle_options_view_limit_changed(y_max_changed=True))
        self._options_view.xAxisLimitsChanged.connect(self._handle_options_view_limit_changed(x_min_changed=True, x_max_changed=True))
        self._options_view.yAxisLimitsChanged.connect(self._handle_options_view_limit_changed(y_min_changed=True, y_max_changed=True))

        self._options_view.secondaryXAxisLowerLimitChanged.connect(self._handle_options_view_secondary_limit_changed(x_min_changed=True))
        self._options_view.secondaryXAxisUpperLimitChanged.connect(self._handle_options_view_secondary_limit_changed(x_max_changed=True))
        self._options_view.secondaryYAxisLowerLimitChanged.connect(self._handle_options_view_secondary_limit_changed(y_min_changed=True))
        self._options_view.secondaryYAxisUpperLimitChanged.connect(self._handle_options_view_secondary_limit_changed(y_max_changed=True))
        self._options_view.secondaryXAxisLimitsChanged.connect(self._handle_options_view_secondary_limit_changed(x_min_changed=True, x_max_changed=True))
        self._options_view.secondaryYAxisLimitsChanged.connect(self._handle_options_view_secondary_limit_changed(y_min_changed=True, y_max_changed=True))
    
    def setLegendControl(self, legend_control):
        self._legend_control = legend_control
        self._legend_control.seriesUpdated.connect(self._legend_series_updated)
        self._legend_control.showLegendChanged.connect(self._show_legend)
        self._legend_control.seriesNameChanged.connect(self._handle_series_name_changed)
        self._legend_control.showSeriesChanged.connect(self._handle_show_series_changed)
        bind(self._legend_control, self, 'hasHiddenSeries', two_way=False)

    def _legend_series_updated(self):
        if self._legend is not None:
            self._show_legend(self._legend_control.showLegend)

    def _show_legend(self, show):
        if self._legend and not show:
            self._legend.remove()
            self._legend = None
            self.draw()
        elif show:
            if self._legend:
                self._legend.remove()
            show_series = self._legend_control.showSeries
            handles = [h for h, s in zip(self._legend_control.seriesHandles, show_series) if s]
            names = [n for n, s in zip(self._legend_control.seriesNames, show_series) if s]
            axes = (
                self._secondary_axes
                if self._secondary_axes
                and self._secondary_axes.get_visible()
                and self._secondary_axes.get_zorder() > self._axes.get_zorder()
                else self._axes
            )
            self._legend = self._create_legend(axes, handles, names, markerscale=self._get_legend_markerscale())
            if self._get_legend_text_color() is not None:
                for text in self._legend.texts:
                    text.set_color(self._get_legend_text_color())
            self._draggable_legend = DraggableLegend(self._legend)
            self.draw()
        
    def _get_legend_markerscale(self):
        return 5
    
    def _create_legend(self, axes, handles, names, **kwargs):
        return axes.legend(handles, names, **kwargs)
    
    def _get_legend_text_color(self):
        return None
    
    def _handle_series_name_changed(self, index, series_name):
        if self._legend is not None and index < len(self._legend_control.seriesHandles):
            visible_handles = [h for h, s in zip(self._legend_control.seriesHandles, self._legend_control.showSeries) if s and h is not None]
            try:
                legend_index = visible_handles.index(self._legend_control.seriesHandles[index])
            except ValueError:
                return
            if legend_index < len(self._legend.texts):
                self._legend.texts[legend_index].set_text(series_name)
                self.draw()
    
    def _handle_show_series_changed(self, index, show_series):
        if index < len(self._legend_control.seriesHandles):
            self._set_series_visibility(self._legend_control.seriesHandles[index], show_series)
        if self._legend is not None:
            self._show_legend(self._legend_control.showLegend)
        else:
            self.draw()

    def _set_series_visibility(self, handle, visible):
        if not handle:
            return
        if hasattr(handle, 'set_visible'):
            handle.set_visible(visible)
        elif hasattr(handle, 'get_children'):
            for child in handle.get_children():
                self._set_series_visibility(child, visible)

    def _do_update_grid_lines(self, axes):
        show_grid_lines = self._options_view and self._options_view.showGridLines
        gridline_color = axes.spines[list(axes.spines.keys())[0]].get_edgecolor()
        gridline_color = gridline_color[0], gridline_color[1], gridline_color[2], 0.5
        kwargs = dict(color=gridline_color, alpha=0.5) if show_grid_lines else {}
        axes.grid(show_grid_lines, **kwargs)
        self.draw()

    def _update_grid_lines(self):
        self._do_update_grid_lines(self._axes)

    def _handle_options_view_limit_changed(self, x_min_changed=False, x_max_changed=False, y_min_changed=False, y_max_changed=False):
        def _():
            if self._options_view is None or self._setting_axis_limits:
                return
            (x_min, x_max), (y_min, y_max) = (new_x_min, new_x_max), (new_y_min, new_y_max) = self._get_xy_extents()
            (x_opt_min, x_opt_max), (y_opt_min, y_opt_max) = self._get_options_view_xy_extents()
            if x_min_changed:
                new_x_min = x_opt_min
            if x_max_changed:
                new_x_max = x_opt_max
            if y_min_changed:
                new_y_min = y_opt_min
            if y_max_changed:
                new_y_max = y_opt_max
            if [new_x_min, new_x_max, new_y_min, new_y_max] != [x_min, x_max, y_min, y_max]:
                self._xy_extents = (new_x_min, new_x_max), (new_y_min, new_y_max)
                self._set_axes_limits()
                self.draw()
        return _
    
    def _get_options_view_xy_extents(self):
        (x_data_min, x_data_max), (y_data_min, y_data_max) = self._get_data_xy_extents()
        x_min = x_data_min if np.isnan(self._options_view.xAxisLowerLimit) else self._options_view.xAxisLowerLimit
        x_max = x_data_max if np.isnan(self._options_view.xAxisUpperLimit) else self._options_view.xAxisUpperLimit
        y_min = y_data_min if np.isnan(self._options_view.yAxisLowerLimit) else self._options_view.yAxisLowerLimit
        y_max = y_data_max if np.isnan(self._options_view.yAxisUpperLimit) else self._options_view.yAxisUpperLimit
        return (x_min, x_max), (y_min, y_max)

    def _handle_options_view_secondary_limit_changed(self, x_min_changed=False, x_max_changed=False, y_min_changed=False, y_max_changed=False):
        def _():
            if self._options_view is None or self._setting_axis_limits:
                return
            updated = False
            (x_opt_min, x_opt_max), (y_opt_min, y_opt_max) = self._get_options_view_secondary_xy_extents()
            if self._has_secondary_y_extent() and (y_min_changed or y_max_changed):
                y_min, y_max = new_y_min, new_y_max = self._get_secondary_y_extent()
                if y_min_changed:
                    new_y_min = y_opt_min
                if y_max_changed:
                    new_y_max = y_opt_max
                if [new_y_min, new_y_max] != [y_min, y_max]:
                    self._secondary_y_extent = (new_y_min, new_y_max)
                    updated = True
            if self._has_secondary_x_extent() and (x_min_changed or x_max_changed):
                x_min, x_max = new_x_min, new_x_max = self._get_secondary_x_extent()
                if x_min_changed:
                    new_x_min = x_opt_min
                if x_max_changed:
                    new_x_max = x_opt_max
                if [new_x_min, new_x_max] != [x_min, x_max]:
                    self._secondary_x_extent = (new_x_min, new_x_max)
                    updated = True
            if updated:
                self._set_axes_limits()
                self.draw()
        return _

    def _get_options_view_secondary_xy_extents(self):
        x_data_min, x_data_max = self._get_data_secondary_x_extent()
        y_data_min, y_data_max = self._get_data_secondary_y_extent()
        x_min = x_data_min if np.isnan(self._options_view.secondaryXAxisLowerLimit) else self._options_view.secondaryXAxisLowerLimit
        x_max = x_data_max if np.isnan(self._options_view.secondaryXAxisUpperLimit) else self._options_view.secondaryXAxisUpperLimit
        y_min = y_data_min if np.isnan(self._options_view.secondaryYAxisLowerLimit) else self._options_view.secondaryYAxisLowerLimit
        y_max = y_data_max if np.isnan(self._options_view.secondaryYAxisUpperLimit) else self._options_view.secondaryYAxisUpperLimit
        return (x_min, x_max), (y_min, y_max)

    def _on_data_changed(self):
        self._cached_label_width_height = None

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        if event.isAccepted():
            self._zoom_selector.onselect = self._span.onselect = self._span._select_none_handler = None

    def set_divider_h_margin(self, h_margin):
        h = [Size.Fixed(h_margin[0]), Size.Scaled(1.0), Size.Fixed(h_margin[1])]
        self._divider.set_horizontal(h)

    def set_divider_v_margin(self, v_margin):
        v = [Size.Fixed(v_margin[0]), Size.Scaled(1.0), Size.Fixed(v_margin[1])]
        self._divider.set_vertical(v)

    @property
    def x_extent_padding(self):
        return self._x_extent_padding
    
    @x_extent_padding.setter
    def x_extent_padding(self, value):
        self._x_extent_padding = value
    
    @property
    def y_extent_padding(self):
        return self._y_extent_padding
    
    @y_extent_padding.setter
    def y_extent_padding(self, value):
        self._y_extent_padding = value

    def _in_interval(self, value, interval):
        return interval[0] <= value <= interval[1]

    def _interval_skew(self, value, interval):
        return (value - interval[0]) / (interval[1] - interval[0])
    
    def _in_x_scroll_zone(self, event):
        return self._in_interval(event.x, self._axes.bbox.intervalx) and event.y <= self._axes.bbox.intervaly[1]
    
    def _in_y_scroll_zone(self, event):
        return self._in_interval(event.y, self._axes.bbox.intervaly) and event.x <= self._axes.bbox.intervalx[1]

    def _on_scroll(self, event):
        if self._secondary_axes is not None:
            self._handle_scroll_secondary(event)
        in_x = self._in_x_scroll_zone(event)
        in_y = self._in_y_scroll_zone(event)
        if in_x or in_y and event.button in ['up', 'down']:
            (x_min, x_max), (y_min, y_max) = self._get_actual_xy_extents()
            if (in_x and self._single_axis_zoom_enabled) or (in_x and in_y):
                skew = self._zoom_skew and self._zoom_skew[0]
                skew = self._interval_skew(event.x, self._axes.bbox.intervalx) if skew is None else skew
                x_min, x_max = self._zoom(x_min, x_max, skew, event.button)
            if (in_y and self._single_axis_zoom_enabled) or (in_x and in_y):
                skew = self._zoom_skew and self._zoom_skew[1]
                skew = self._interval_skew(event.y, self._axes.bbox.intervaly) if skew is None else skew
                y_min, y_max = self._zoom(y_min, y_max, skew, event.button)
            self._xy_extents = (x_min, x_max), (y_min, y_max)
        self._set_axes_limits()
        self.draw()
    
    def _in_secondary_y_scroll_zone(self, event):
        return self._in_interval(event.y, self._axes.bbox.intervaly) and \
                event.x >= self._axes.bbox.intervalx[1]

    def _in_secondary_x_scroll_zone(self, event):
        return self._in_interval(event.x, self._axes.bbox.intervalx) and \
                event.y >= self._axes.bbox.intervaly[1]

    def _handle_scroll_secondary(self, event):
        if self._has_secondary_y_extent():
            in_secondary_y = self._in_secondary_y_scroll_zone(event)
            if in_secondary_y and event.button in ['up', 'down']:
                self._secondary_y_extent = self._zoom(
                    *self._get_secondary_y_extent(),
                    self._interval_skew(event.y, self._axes.bbox.intervaly),
                    event.button
                )
        if self._has_secondary_x_extent():
            in_secondary_x = self._in_secondary_x_scroll_zone(event)
            if in_secondary_x and event.button in ['up', 'down']:
                self._secondary_x_extent = self._zoom(
                    *self._get_secondary_x_extent(),
                    self._interval_skew(event.x, self._axes.bbox.intervalx),
                    event.button
                )

    def _get_zoom_multiplier(self):
        return 20/19
    
    def _zoom(self, min_, max_, skew, direction):
        zoom_multiplier = self._get_zoom_multiplier() if direction == 'up' else 1 / self._get_zoom_multiplier()
        range_ = max_ - min_
        diff = (range_ * (1/zoom_multiplier)) - range_
        max_ += diff * (1 - skew)
        min_ -= diff * skew
        return min_, max_
    
    def _ensure_x_limit(self, _axes, x_limit):
        return float(x_limit)

    def _do_set_axes_limits(self, axes):
        try:
            self._setting_axis_limits = True
            if self._secondary_axes is not None:
                self._set_secondary_axes_limits()
            self._update_ticks()
            (x_min, x_max), (y_min, y_max) = self._get_xy_extents()
            if self._options_view is not None:
                if self._options_view.x_limits:
                    self._options_view.setXLimits(
                        self._ensure_x_limit(axes, x_min),
                        self._ensure_x_limit(axes, x_max))
                if self._options_view.y_limits:
                    self._options_view.setYLimits(float(y_min), float(y_max))
            axes.set_xlim(*_safe_limits(x_min, x_max))
            axes.set_ylim(*_safe_limits(y_min, y_max))
        finally:
            self._setting_axis_limits = False

    def _set_axes_limits(self):
        self._do_set_axes_limits(self.axes)

    def _set_secondary_axes_limits(self):
        if self._options_view is not None:
            if self._options_view.secondary_y_limits:
                enabled = self._secondary_y_enabled()
                secondary_y_min, secondary_y_max = self._get_secondary_y_extent() if enabled else (float('nan'), float('nan'))
                self._options_view.setSecondaryYLimitsEnabled(enabled)
                self._options_view.setSecondaryYLimits(float(secondary_y_min), float(secondary_y_max))
            if self._options_view.secondary_x_limits:
                enabled = self._secondary_x_enabled()
                secondary_x_min, secondary_x_max = self._get_secondary_x_extent() if enabled else (float('nan'), float('nan'))
                self._options_view.setSecondaryXLimitsEnabled(enabled)
                self._options_view.setSecondaryXLimits(float(secondary_x_min), float(secondary_x_max))
        if self._has_secondary_y_extent():
            self._secondary_axes.set_ylim(*_safe_limits(*self._get_secondary_y_extent()))
        if self._has_secondary_x_extent():
            self._secondary_axes.set_xlim(*_safe_limits(*self._get_secondary_x_extent()))
    
    def _secondary_y_enabled(self):
        return True if self._secondary_axes and self._secondary_axes.get_visible() and self._has_secondary_y_extent() else False

    def _secondary_x_enabled(self):
        return True if self._secondary_axes and self._secondary_axes.get_visible() and self._has_secondary_x_extent() else False

    def _set_axes_labels(self):
        self._axes.set_xlabel(self.data.xAxisTitle)
        self._axes.set_ylabel(self.data.yAxisTitle)
    
    def _set_center(self, center):
        if not all(c is not None for c in center):
            center = (0, 0)
        x_extent, y_extent = self._get_xy_extents()
        span = x_extent[1] - x_extent[0], y_extent[1] - y_extent[0]
        x_extent = center[0] - span[0] / 2, center[0] + span[0] / 2
        y_extent = center[1] - span[1] / 2, center[1] + span[1] / 2
        self._xy_extents = x_extent, y_extent

    def _get_xy_extents(self):
        if self.data is None:
            return (0, 0), (0, 0)
        if self._xy_extents is None:
            return self._get_data_xy_extents()
        return self._xy_extents
    
    def _get_data_xy_extents(self):
        if self.data is None:
            return (0, 0), (0, 0)
        (x_min, x_max), (y_min, y_max) = self.data.get_xy_extents()
        return self._pad_extent(x_min, x_max, self.x_extent_padding), self._pad_extent(y_min, y_max, self.y_extent_padding)
    
    def _has_secondary_y_extent(self):
        return hasattr(self.data, 'get_secondary_y_extent')
    
    def _get_secondary_y_extent(self):
        if self._secondary_y_extent is not None:
            return self._secondary_y_extent
        if self.data is not None:
            return self._get_data_secondary_y_extent()
        return (0, 0)
    
    def _get_data_secondary_y_extent(self):
        if self.data is None:
            return (0, 0)
        return self._pad_extent(*self.data.get_secondary_y_extent(), self.y_extent_padding)
    
    def _has_secondary_x_extent(self):
        return hasattr(self.data, 'get_secondary_x_extent')

    def _get_secondary_x_extent(self):
        if self._secondary_x_extent is not None:
            return self._secondary_x_extent
        if self.data is not None:
            return self._get_data_secondary_x_extent()
        return (0, 0)
    
    def _get_data_secondary_x_extent(self):
        if self.data is None or not hasattr(self.data, 'get_secondary_x_extent'):
            return (0, 0)
        return self._pad_extent(*self.data.get_secondary_x_extent(), self.x_extent_padding)

    def _get_actual_xy_extents(self):
        return self._axes.get_xlim(), self._axes.get_ylim()
    
    def _pad_extent(self, min_, max_, padding):
        min_, max_ = self._zero_if_nan(min_), self._zero_if_nan(max_)
        range_ = max_ - min_
        return min_ - padding * range_, max_ + padding * range_

    def _zoom_selected(self, start_pos, end_pos):
        x_min, x_max = min(start_pos.xdata, end_pos.xdata), max(start_pos.xdata, end_pos.xdata)
        y_min, y_max = min(start_pos.ydata, end_pos.ydata), max(start_pos.ydata, end_pos.ydata)
        self._xy_extents = (x_min, x_max), (y_min, y_max)
        self._set_axes_limits()
        self.draw()

    def _handle_span_select(self, x_min, x_max):
        x_min, x_max = self._round_to_bin_width(x_min, x_max)
        self._update_span_rect(x_min, x_max)
        self.span = SpanModel(self, x_min, x_max)
        self.draw()

    def _handle_span_select_none(self):
        self.span = None

    def _handle_press(self, event):
        if event.button == 1:
            if self._is_panning:
                self._pan_event = event
            elif self._span.active:
                self._handle_span_press(event)
    
    def _handle_move(self, event):
        if event.xdata and self._pan_event:
            self._handle_pan_move(event)
        elif event.xdata and any(self._span_events()):
            self._handle_span_move(event)

    def _handle_release(self, event):
        if self._pan_event:
            self._pan_event = None
        elif any(self._span_events()):
            self._handle_span_release(event)

    def _handle_pan_move(self, event):
        from_x, from_y = self._axes.transData.inverted().transform((self._pan_event.x, self._pan_event.y))
        to_x, to_y = self._axes.transData.inverted().transform((event.x, event.y))
        self._pan(from_x - to_x, from_y - to_y)
        self._pan_event = event

    def _pan(self, delta_x, delta_y):
        (x_min, x_max), (y_min, y_max) = self._get_xy_extents()
        self._xy_extents = (x_min + delta_x, x_max + delta_x), (y_min + delta_y, y_max + delta_y)
        self._set_axes_limits()
        self.draw()

    def _span_events(self):
        return self._span_center_mouse_event, self._span_left_mouse_event, self._span_right_mouse_event

    def _handle_span_press(self, event):
        if not event.xdata:
            return
        span_min, span_max = (self.span.left, self.span.right) if self.span else (0, 0)
        edge_tolerance = self._span_tolerance()
        if abs(span_min - event.xdata) < edge_tolerance:
            self._span.active = False
            self._span_left_mouse_event = event
        elif abs(span_max - event.xdata) < edge_tolerance:
            self._span.active = False
            self._span_right_mouse_event = event
        elif span_min < event.xdata < span_max:
            self._span.active = False
            self._span_center_mouse_event = event
    
    def _handle_span_move(self, event):
        if not self.span:
            return
        x_min, x_max = self.span.left, self.span.right
        last_event = next(x for x in self._span_events() if x)
        diff_x = event.xdata - last_event.xdata
        if self._span_center_mouse_event is not None:
            self._update_span_rect(x_min + diff_x)
        elif self._span_left_mouse_event is not None:
            self._update_span_rect(x_min + diff_x, x_max)
        elif self._span_right_mouse_event is not None:
            self._update_span_rect(x_min, x_max + diff_x)
        self.draw([self._span.rect])
    
    def _handle_span_release(self, _event):
        x_min = self._span.rect.get_x()
        x_max = x_min + self._span.rect.get_width()
        x_min, x_max = self._round_to_bin_width(x_min, x_max)
        self._update_span_rect(x_min, x_max)
        self.span = SpanModel(self, x_min, x_max)
        self.draw()
        self._span.active = True
        self._span_center_mouse_event = self._span_left_mouse_event = self._span_right_mouse_event = None

    def _do_update_span_rect(self, span_tool, x_min, x_max):
        if span_tool is None:
            return
        span_tool.rect.set_x(x_min)
        if x_max:
            span_tool.rect.set_width(x_max - x_min)
        span_tool.handles.set_data(span_tool.extents)

    def _update_span_rect(self, x_min, x_max=None):
        self._do_update_span_rect(self._span, x_min, x_max)
    
    def _round_to_bin_width(self, x_min, x_max):
        return x_min, x_max
    
    def _span_tolerance(self):
        return 5

    def toolEnabled(self, _tool_type):
        return False

    def toolAvailable(self, _tool_type):
        return False

    def _activate_span_tool(self, span_tool, active, axes=None):
        if span_tool.active and not active:
            self._previous_span = self.span
            self.span = None
            for r in [span_tool.rect]:
                self._remove_artist(r)
        elif not span_tool.active and active:
            self.span = self._previous_span
            for r in [span_tool.rect]:
                self._add_artist(r, axes=axes)
        span_tool.active = active
        self.draw()
        
    def activateTool(self, tool_type, active):
        if tool_type == ToolType.zoom:
            self._zoom_selector.set_active(active)
            if not active:
                self._zoom_selector.clear()
        elif tool_type == ToolType.span:
            self._activate_span_tool(self._span, active)
        elif tool_type == ToolType.pan:
            self._is_panning = active
        self._active_tools[tool_type] = active
    
    def toolActive(self, tool_type):
        return self._active_tools.get(tool_type, False)
    
    def isActiveDefault(self, _tool_type):
        return False

    def _add_artist(self, artist, axes=None):
        axes = axes or self._axes
        axes.add_artist(artist)
        self._decoration_artists.append(artist)
    
    def _remove_artist(self, artist):
        artist.remove()
        if artist in self._decoration_artists:
            self._decoration_artists.remove(artist)
    
    def _handle_resize(self, _event):
        self._update_ticks()
        return self.draw()


    def _draw(self, artists=None, axes=None):
        if artists is None:
            def _update():
                for a in self._decoration_artists:
                    a.remove()
                self._canvas.draw()
                self._background_cache = self._canvas.copy_from_bbox(self._figure.bbox)
                for a in self._decoration_artists:
                    axes.add_artist(a)
                    axes.draw_artist(a)
                self._canvas.update()
            self._pending_draw = _update
        else:
            def _update():
                if self._background_cache is None:
                    raise RuntimeError('Must run draw before drawing artists!')
                self._canvas.restore_region(self._background_cache)
                for a in artists:
                    axes.draw_artist(a)
                self._canvas.update()
            self._pending_artists_draw = _update

    def draw(self, artists=None):
        return self._draw(artists, self._axes)

    def _do_draw_events(self):
        if self._pending_draw is not None:
            self._pending_draw()
            self._pending_draw = None
        if self._pending_artists_draw is not None:
            self._pending_artists_draw()
            self._pending_artists_draw = None
        if self._other_draw_events:
            for draw_event in self._other_draw_events:
                draw_event()
            self._other_draw_events = []

    def addDrawEvent(self, draw_event):
        self._other_draw_events.append(draw_event)

    def resetZoom(self):
        self._secondary_y_extent = self._secondary_x_extent = None
        self._xy_extents = None
        self._set_axes_limits()
        self.draw()
    
    def _twinx(self, ylabel):
        axes = self._axes.twinx()
        for spine in ['top', 'left']:
            axes.spines[spine].set_visible(False)
        axes.set_ylabel(ylabel)
        axes.set_zorder(1)
        return axes
    
    @property
    def axes(self):
        return self._axes

    @property
    def secondary_axes(self):
        if self._secondary_axes is None:
            self._set_secondary_axes(self._twinx(''))
        return self._secondary_axes
    
    def _set_secondary_axes(self, axes):
        self._secondary_axes = axes

    @staticmethod
    def sizeHint():
        """function::sizeHint()
        Override the default sizeHint to ensure the plot has an initial size
        """
        return QSize(600, 400)

    def minimumSizeHint(self):
        """function::sizeHint()
        Override the default sizeHint to ensure the plot does not shrink below minimum size
        """
        return self.sizeHint()

    @staticmethod
    def _zero_if_nan(value):
        return value if not isinstance(value, float) or not np.isnan(value) else 0
    
    def canShowTable(self):
        return hasattr(self, 'data') and self.data is not None and hasattr(self.data, 'table')

    def contextMenuEvent(self, event):
        self._show_table_action.setEnabled(self.canShowTable())
        self._menu.exec_(event.globalPos())

    def copyToClipboard(self):
        with BytesIO() as buffer:
            self._figure.savefig(buffer, facecolor=self._figure.get_facecolor())
            QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def saveAsImage(self):
        filename = self._file_dialog_service.get_save_filename(self, self.tr('Portable Network Graphics (*.png)'))
        if filename:
            self._figure.savefig(filename, facecolor=self._figure.get_facecolor())

    def showTable(self):
        if self.canShowTable():
            self._table_view = TableView(None)
            self._table_view.pasteEnabled = False
            self._table_view.setModel(self.data.table)
            self._table_view.setMinimumSize(800, 600)
            self._table_view.show()

    def _update_ticks(self):
        if not self.data:
            return
        if hasattr(self.data, 'x_labels'):
            step = self.data.x_tick_interval if hasattr(self.data, 'x_tick_interval') else None
            x_ticks, x_labels, x_ticks_rotation = self._get_labels(self.data.x_labels, step, horizontal=True)
            self._axes.set_xticks(x_ticks)
            if hasattr(self.data, 'x_ticks_rotation'):
                rotation = x_ticks_rotation if np.isnan(self.data.x_ticks_rotation) else self.data.x_ticks_rotation
                self._axes.set_xticklabels(
                    x_labels, rotation=rotation, ha='right' if rotation else 'center')
                self._adjust_to_xticklabels_height(x_labels, rotation)
            else:
                self._axes.set_xticklabels(x_labels)

        if hasattr(self.data, 'y_labels'):
            step = self.data.y_tick_interval if hasattr(self.data, 'y_tick_interval') else None
            y_ticks, y_labels, _ = self._get_labels(self.data.y_labels, step, horizontal=False)
            self._axes.set_yticks(y_ticks)
            self._axes.set_yticklabels(y_labels)
            self._adjust_to_yticklabels_width(y_labels)

    def _adjust_to_yticklabels_width(self, labels):
        sizes = self._divider.get_horizontal()
        ticklabels_font_family = self._axes.yaxis.get_ticklabels()[0].get_family() if labels else None
        ticklabels_font_size = self._axes.yaxis.get_ticklabels()[0].get_size() if labels else None
        width, _ = self._get_labels_width_height(
            labels, font_family=ticklabels_font_family, font_size=ticklabels_font_size)

        ylabel_font_family = self._axes.yaxis.get_label().get_family()
        ylabel_font_size = self._axes.yaxis.get_label().get_size()
        y_label_width, _ = self._get_labels_width_height(
            [self._axes.get_ylabel()], font_family=ylabel_font_family, font_size=ylabel_font_size, rotation=90)
     
        width += y_label_width + 0.3 * self._figure.dpi # Need this offset to account for the tick marks and ylabel
        sizes[0] = Size.Fixed(width / self._figure.dpi)
        self._divider.set_horizontal(sizes)
        self.yTickLabelsWidthAdjusted.emit()

    def _adjust_to_xticklabels_height(self, labels, rotation=None):
        sizes = self._divider.get_vertical()
        ticklabels_font_family = self._axes.xaxis.get_ticklabels()[0].get_family() if labels else None
        ticklabels_font_size = self._axes.xaxis.get_ticklabels()[0].get_size() if labels else None
        _, height = self._get_labels_width_height(
            labels, font_family=ticklabels_font_family, font_size=ticklabels_font_size, rotation=rotation)
        
        xlabel_font_family = self._axes.xaxis.get_label().get_family()
        xlabel_font_size = self._axes.xaxis.get_label().get_size()
        _, x_label_height = self._get_labels_width_height(
            [self._axes.get_xlabel()], font_family=xlabel_font_family, font_size=xlabel_font_size)
        
        height += x_label_height + 0.2 * self._figure.dpi # Need this offset to account for the tick marks and xlabel
        sizes[0] = Size.Fixed(height / self._figure.dpi)
        self._divider.set_vertical(sizes)

    def _get_labels(self, labels, step, horizontal=True):
        (x0, x1), (y0, y1) = self._get_xy_extents()
        start, end = (int(x0), int(x1)) if horizontal else (int(y0), int(y1))
        visible_points = end - start
        labels_rotation = None
        axes_bbox = self._axes.get_window_extent(self._figure.canvas.get_renderer()).transformed(self._figure.dpi_scale_trans.inverted())
        plot_size = (axes_bbox.width if horizontal else axes_bbox.height) * self._figure.dpi
        width, height = self._get_labels_width_height(labels)
        size = (width if horizontal else height)
        if not (step and step > 0):
            if plot_size == 0 or size == 0:
                n_labels = 16
            else:
                n_labels = int(plot_size / size)
                if n_labels == 0:
                    n_labels = 16
            step = int(visible_points / n_labels) + 1
        else:
            step = int(step)
        if horizontal and (visible_points / step) * size > plot_size:
            labels_rotation = 30
        indexes = list(range(len(labels)))
        display_labels = list(labels)
        for i in indexes:
            if i % step:
                display_labels[i] = ''
        return indexes, display_labels, labels_rotation

    def _get_labels_width_height(self, labels, font_family=None, font_size=None, rotation=None):
        self._cached_label_width_height = self._cached_label_width_height or {}
        cache_key = (tuple(labels), ''.join([str(i) for i in (font_family, font_size)]))
        if cache_key not in self._cached_label_width_height:
            font = MatPlotLibFont(font=font_family) if font_family else MatPlotLibFont.default()
            width = 0
            height = 0
            font_size = font_size or matplotlib.rcParams['font.size']
            for label in labels:
                next_width, next_height = font.get_size(str(label), font_size, self._figure.dpi)
                width = max(width, next_width)
                height = max(height, next_height)
            self._cached_label_width_height[cache_key] = width, height
        width, height = self._cached_label_width_height[cache_key]
        return (abs(width * np.cos(np.radians(rotation))), abs(width * np.sin(np.radians(rotation)) + height)) if rotation is not None else (width, height)

    def _create_new_axes(self, nx=1, ny=1) -> Axes:
        axes = Axes(self._figure, self._divider.get_position())
        axes.set_axes_locator(self._divider.new_locator(nx=nx, ny=ny))
        self._figure.add_axes(axes)
        return axes
    
    @staticmethod
    def _create_secondary_xy_axes(figure, divider, nx=1, ny=1, visible=False, z_order=1):
        axes = Axes(figure, divider.get_position())
        axes.set_axes_locator(divider.new_locator(nx=nx, ny=ny))
        axes.xaxis.tick_top()
        axes.xaxis.set_label_position('top')
        axes.yaxis.tick_right()
        axes.yaxis.set_label_position('right')
        axes.patch.set_visible(visible)
        axes.set_zorder(z_order)
        figure.add_axes(axes)
        axes.ticklabel_format(style='sci', axis='x', scilimits=(-4, 4))
        axes.ticklabel_format(style='sci', axis='y', scilimits=(-4, 4))
        return axes

    @staticmethod
    def _create_shared_axes(figure, divider, shared_axes, nx=1, ny=1, visible=False, z_order=1):
        axes = Axes(figure, divider.get_position(), sharex=shared_axes, sharey=shared_axes, frameon=False)
        axes.set_axes_locator(divider.new_locator(nx=nx, ny=ny))
        for spine in axes.spines.values():
            spine.set_visible(False)
        for axis in axes.axis.values():
            axis.set_visible(False)
        axes.patch.set_visible(False)
        axes.set_visible(False)
        axes.set_zorder(z_order)
        figure.add_axes(axes)
        return axes
