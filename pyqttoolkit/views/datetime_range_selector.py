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
""":mod:`datetime_range_selector`
Defines the DatetimeRangeSelectorWidget
"""
import weakref

from PyQt5.QtCore import pyqtSignal, QDateTime, QSize
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QMenu, QAction, QPushButton

from datetime import timedelta, datetime
from typing import Optional, Tuple

from pyqttoolkit.properties import auto_property, bind, unbind
from pyqttoolkit.datetime.qdatetime import step_qdatetime
from pyqttoolkit.services.link_manager import IncompatibleWidgets
from .linkable import LinkableWidget
from .datetime import DateTimeEdit
from .icon_button import IconButton

class DatetimeRangeSelectorWidget(LinkableWidget):
    """class::DatetimeRangeSelectorWidget
    Widget to select a datetime range
    """
    def __init__(self, parent, paging=False, link_manager=None, reset_enabled=True, link_type=None,
                    update_limits_on_value_change: bool = True,
                    default_limits: Optional[Tuple[datetime, datetime]]=None,
                    set_to_limit_buttons: bool = False):
        LinkableWidget.__init__(self, parent, link_manager, link_type)
        self._date_range_start = self._date_range_end = None
        self._interval = None
        self._update_limits_on_value_change = update_limits_on_value_change
        
        if paging:
            self._back_one = IconButton('left.svg', self.tr('Scroll Left'), self, QSize(8, 30))
            self._back_one.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self._back_one.clicked.connect(self._step(-1))
        self._from_selector = DateTimeEdit(self, DateTimeEdit.Limit.min)
        self._to_selector = DateTimeEdit(self, DateTimeEdit.Limit.max)
        if default_limits:
            self._from_selector.setDateTimeRange(*default_limits)
            self._to_selector.setDateTimeRange(*default_limits)
        if paging:
            self._forward_one = IconButton('right.svg', self.tr('Scroll Right'), self, QSize(8, 30))
            self._forward_one.clicked.connect(self._step(1))
            self._forward_one.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._from_selector, 0, 1)
        self._layout.addWidget(self._to_selector, 1, 1)

        if paging:
            self._layout.addWidget(self._back_one, 0, 0, 2, 1)
            self._layout.addWidget(self._forward_one, 0, 2, 2, 1)

        if set_to_limit_buttons:
            self._set_to_start = QPushButton(self.tr('Set to Start'), self)
            self._set_to_start.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self._set_to_start.setFixedWidth(65)
            self._set_to_end = QPushButton(self.tr('Set to End'), self)
            self._set_to_end.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self._set_to_end.setFixedWidth(65)

            self._layout.addWidget(self._set_to_start, 0, 2)
            self._layout.addWidget(self._set_to_end, 1, 2)

            def _handle_set_to_limit_clicked(widget, prop):
                view_ref = weakref.ref(self)
                def _():
                    view = view_ref()
                    if view:
                        widget.reset()
                        prop.__get__(view).emit(widget.value)
                return _

            self._set_to_start.clicked.connect(
                _handle_set_to_limit_clicked(
                    self._from_selector, DatetimeRangeSelectorWidget.dateFromChanged))
            self._set_to_end.clicked.connect(
                _handle_set_to_limit_clicked(
                    self._to_selector, DatetimeRangeSelectorWidget.dateToChanged))

        self._from_selector.editingFinished.connect(self._date_from_editing_finished)
        self._to_selector.editingFinished.connect(self._date_to_editing_finished)

        self._menu = QMenu(self)
        self._reset = QAction(self.tr('Reset'), self)
        self._reset.triggered.connect(self._handle_reset)
        self._menu.addAction(self._reset)
        self._reset_enabled = reset_enabled

    dateFromChanged = pyqtSignal(QDateTime)
    dateToChanged = pyqtSignal(QDateTime)
    datesChanged = pyqtSignal(QDateTime, QDateTime)

    @property
    def date_from_selector(self):
        return self._from_selector

    @property
    def date_to_selector(self):
        return self._to_selector

    def contextMenuEvent(self, event):
        if self._reset_enabled:
            self._menu.exec_(event.globalPos())
        
    def _handle_reset(self):
        self.setDates(self._date_range_start, self._date_range_end)

    def link(self, other):
        if not isinstance(other, DatetimeRangeSelectorWidget):
            raise IncompatibleWidgets()
        bind(self, other, 'dateFrom')
        bind(self, other, 'dateTo')
        self.datesChanged.connect(other.setDates)
        other.datesChanged.connect(self.setDates)
    
    def unlink(self, other):
        unbind(self, other, 'dateFrom')
        unbind(self, other, 'dateTo')
        self.datesChanged.disconnect(other.setDates)
        other.datesChanged.disconnect(self.setDates)

    def setDates(self, dateFrom, dateTo):
        if self.dateFrom != dateFrom or self.dateTo != dateTo:
            signals_blocked = self.blockSignals(True)
            self.dateFrom = dateFrom
            self.dateTo = dateTo
            self.blockSignals(signals_blocked)
            self.datesChanged.emit(dateFrom, dateTo)

    def setDateRange(self, start_date, end_date):
        """function::setDateRange(self, start_data, end_date)
        Set the date range for this widget
        """
        self._from_selector.setDateTimeRange(start_date, end_date)
        self._to_selector.setDateTimeRange(start_date, end_date)
        self._date_range_start = start_date
        self._date_range_end = end_date
    
    def setInterval(self, interval):
        self._interval = interval

        if interval < timedelta(seconds=1):
            display_format = 'dd-MMM-yyyy hh:mm:ss.zz'
        elif interval < timedelta(minutes=1):
            display_format = 'dd-MMM-yyyy hh:mm:ss'
        else:
            display_format = 'dd-MMM-yyyy hh:mm'

        for selector in self._from_selector, self._to_selector:
            selector.setDisplayFormat(display_format)

    @auto_property(QDateTime)
    def dateFrom(self):
        """function::dateFrom(self)
        Auto property accessor for dateFrom
        """
        return self._from_selector.dateTime()

    @dateFrom.setter
    def dateFrom(self, value):
        """function::dateFrom(self, value)
        Auto property setter for dateFrom
        """
        value = value or QDateTime()
        if self._from_selector.dateTime() != value:
            self._from_selector.setDateTime(value)
            self.dateFromChanged.emit(value)

    @auto_property(QDateTime)
    def dateTo(self):
        """function::dateTo(self)
        Auto property accessor for dateTo
        """
        return self._to_selector.dateTime()

    @dateTo.setter
    def dateTo(self, value):
        """function::dateTo(self, value)
        Auto property setter for dateTo
        """
        value = value or QDateTime()
        if self._to_selector.dateTime() != value:
            self._to_selector.setDateTime(value)
            self.dateToChanged.emit(value)

    def sizeHint(self):
        """function::sizeHint(self)
        Override the QWidget.sizeHint method to provide a size hint
        """
        return self._layout.sizeHint()

    def _date_from_editing_finished(self):
        value = self._from_selector.dateTime()
        if self._update_limits_on_value_change:
            self._to_selector.setMinimumDateTime(value)
        self.dateFromChanged.emit(value)

    def _date_to_editing_finished(self):
        value = self._to_selector.dateTime()
        if self._update_limits_on_value_change:
            self._from_selector.setMaximumDateTime(value)
        self.dateToChanged.emit(value)
    
    def _step(self, fraction):
        def _():
            signals_blocked = self.blockSignals(True)
            step_qdatetime(self, fraction, self._interval, self._date_range_start, self._date_range_end)
            self.blockSignals(signals_blocked)
            self.datesChanged.emit(self.dateFrom, self.dateTo)
        return _

    def step(self, fraction):
        return self._step(fraction)()
