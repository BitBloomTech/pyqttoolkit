#pylint: disable=too-many-statements
from io import BytesIO
import numpy as np

#pylint: disable=no-name-in-module
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QVBoxLayout, QWidget, QSize, QTimer, QMenu, QAction, QApplication, QImage, QKeySequence
#pylint: enable=no-name-in-module

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector, SpanSelector
from mpl_toolkits.axes_grid1 import Size, LocatableAxes, Divider

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.models import SpanModel
from pyqttoolkit.views import TableView

from ..tool_type import ToolType
from .font import MatPlotLibFont

class _SpanSeletor(SpanSelector):
    def __init__(self, *args, **kwargs):
        SpanSelector.__init__(self, *args, **kwargs)
        self._select_none_handler = None

    def _release(self, event):
        SpanSelector._release(self, event)
        if self.rect.get_width() < 1:
            self.rect.set_visible(False)
            self.stay_rect.set_visible(False)
            if self._select_none_handler is not None:
                self._select_none_handler()
    
    def set_on_select_none(self, handler):
        self._select_none_handler = handler

class _RectangleSelector(RectangleSelector):
    def _press(self, event):
        if not self.interactive:
            x = event.xdata
            y = event.ydata
            self.extents = x, x, y, y
        RectangleSelector._press(self, event)

class MatPlotLibBase(QWidget):
    def __init__(self,
        parent, file_dialog_service,
        h_margin=(0.8, 0.1), v_margin=(0.5, 0.15),
        h_axes=[Size.Scaled(1.0)], v_axes=[Size.Scaled(1.0)],
        nx_default=1, ny_default=1
        ):
        QWidget.__init__(self, parent)
        self._file_dialog_service = file_dialog_service
        self._figure = Figure()
        self._canvas = FigureCanvas(self._figure)
        h = [Size.Fixed(h_margin[0]), *h_axes, Size.Fixed(h_margin[1])]
        v = [Size.Fixed(v_margin[0]), *v_axes, Size.Fixed(v_margin[1])]
        self._divider = Divider(self._figure, (0.0, 0.0, 1.0, 1.0), h, v, aspect=False)
        self._axes = LocatableAxes(self._figure, self._divider.get_position())
        self._axes.set_axes_locator(self._divider.new_locator(nx=nx_default, ny=ny_default))
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
        
        self._zoom_selector = _RectangleSelector(self._axes, self._zoom_selected)
        self._zoom_selector.set_active(False)
        self._x_extent_padding = 0.01
        self._y_extent_padding = 0.01
        self._axes.ticklabel_format(style='sci', axis='x', scilimits=(-4, 4))
        self._axes.ticklabel_format(style='sci', axis='y', scilimits=(-4, 4))
        self._active_tools = {}
        self._span = _SpanSeletor(
            self._axes, self._handle_span_select, 'horizontal',
            rectprops=dict(alpha=0.2, facecolor='red', edgecolor='k'),
            span_stays=True
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
        self._draw_timer = QTimer()
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

    enabledToolsChanged = pyqtSignal()
    spanChanged = pyqtSignal(SpanModel)

    span = AutoProperty(SpanModel)

    def _on_data_changed(self):
        self._cached_label_width_height = None

    def closeEvent(self, event):
        QWidget.closeEvent(self, event)
        if event.isAccepted():
            self._zoom_selector.onselect = self._span.onselect = None

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

    def _get_zoom_multiplier(self):
        return 20/19
    
    def _zoom(self, min_, max_, skew, direction):
        zoom_multiplier = self._get_zoom_multiplier() if direction == 'up' else 1 / self._get_zoom_multiplier()
        range_ = max_ - min_
        diff = (range_ * (1/zoom_multiplier)) - range_
        max_ += diff * (1 - skew)
        min_ -= diff * skew
        return min_, max_

    def _set_axes_limits(self):
        self._update_ticks()
        (x_min, x_max), (y_min, y_max) = self._get_xy_extents()
        self._axes.set_xlim(x_min, x_max)
        self._axes.set_ylim(y_min, y_max)

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
            (x_min, x_max), (y_min, y_max) = self.data.get_xy_extents()
            return self._pad_extent(x_min, x_max, self.x_extent_padding), self._pad_extent(y_min, y_max, self.y_extent_padding)
        return self._xy_extents

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

    def _update_span_rect(self, x_min, x_max=None):
        self._span.rect.set_x(x_min)
        self._span.stay_rect.set_x(x_min)
        if x_max:
            self._span.rect.set_width(x_max - x_min)
            self._span.stay_rect.set_width(x_max - x_min)
    
    def _round_to_bin_width(self, x_min, x_max):
        return x_min, x_max
    
    def _span_tolerance(self):
        return 5

    def toolEnabled(self, _tool_type):
        return False

    def toolAvailable(self, _tool_type):
        return False

    def activateTool(self, tool_type, active):
        if tool_type == ToolType.zoom:
            self._zoom_selector.set_active(active)
        elif tool_type == ToolType.span:
            if self._span.active and not active:
                self._previous_span = self.span
                self.span = None
                for r in [self._span.rect, self._span.stay_rect]:
                    self._remove_artist(r)
            elif not self._span.active and active:
                self.span = self._previous_span
                for r in [self._span.rect, self._span.stay_rect]:
                    self._add_artist(r)
            self._span.active = active
            self.draw()
        elif tool_type == ToolType.pan:
            self._is_panning = active
        self._active_tools[tool_type] = active
    
    def toolActive(self, tool_type):
        return self._active_tools.get(tool_type, False)
    
    def isActiveDefault(self, _tool_type):
        return False

    def _add_artist(self, artist):
        self._axes.add_artist(artist)
        self._decoration_artists.append(artist)
    
    def _remove_artist(self, artist):
        artist.remove()
        if artist in self._decoration_artists:
            self._decoration_artists.remove(artist)
    
    def _handle_resize(self, _event):
        self._update_ticks()
        return self.draw()

    def draw(self, artists=None):
        if artists is None:
            def _update():
                for a in self._decoration_artists:
                    a.remove()
                self._canvas.draw()
                self._background_cache = self._canvas.copy_from_bbox(self._figure.bbox)
                for a in self._decoration_artists:
                    self._axes.add_artist(a)
                    self._axes.draw_artist(a)
                self._canvas.update()
            self._pending_draw = _update
        else:
            def _update():
                if self._background_cache is None:
                    raise RuntimeError('Must run draw before drawing artists!')
                self._canvas.restore_region(self._background_cache)
                for a in artists:
                    self._axes.draw_artist(a)
                self._canvas.update()
            self._pending_artists_draw = _update
    
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
        self._xy_extents = None
        self._set_axes_limits()
        self.draw()
    
    def _twinx(self, ylabel):
        axes = self._axes.twinx()
        for spine in ['top', 'left']:
            axes.spines[spine].set_visible(False)
        axes.set_ylabel(ylabel)
        return axes

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
            x_ticks, x_labels = self._get_labels(self.data.x_labels, step, horizontal=True)
            self._axes.set_xticks(x_ticks)
            self._axes.set_xticklabels(x_labels)
        if hasattr(self.data, 'y_labels'):
            step = self.data.y_tick_interval if hasattr(self.data, 'y_tick_interval') else None
            y_ticks, y_labels = self._get_labels(self.data.y_labels, step, horizontal=False)
            self._axes.set_yticks(y_ticks)
            self._axes.set_yticklabels(y_labels)

    def _get_labels(self, labels, step, horizontal=True):
        (x0, x1), (y0, y1) = self._get_xy_extents()
        start, end = (int(x0), int(x1)) if horizontal else (int(y0), int(y1))
        visible_points = end - start
        if not (step and step > 0):
            width, height = self._get_label_width_height(labels)
            axes_bbox = self._axes.get_window_extent(self._figure.canvas.get_renderer()).transformed(self._figure.dpi_scale_trans.inverted())
            plot_size = (axes_bbox.width if horizontal else axes_bbox.height) * self._figure.dpi
            size = (width if horizontal else height)
            if plot_size == 0 or size == 0:
                n_labels = 16
            else:
                n_labels = int(plot_size / size)
                if n_labels == 0:
                    n_labels = 16
            step = int(visible_points / n_labels) + 1
        else:
            step = int(step)
        indexes = list(range(len(labels)))
        display_labels = list(labels)
        for i in indexes:
            if i % step:
                display_labels[i] = ''
        return indexes, display_labels
    
    def _get_label_width_height(self, labels):
        if not self._cached_label_width_height:
            font = MatPlotLibFont.default()
            width = 0
            height = 0
            for label in labels:
                next_width, next_height = font.get_size(str(label), matplotlib.rcParams['font.size'], self._figure.dpi)
                width = max(width, next_width)
                height = max(height, next_height)
            self._cached_label_width_height = width, height
        return self._cached_label_width_height