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
#pylint: disable=no-name-in-module
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QDateTime, QSize, QMenu, QAction
from PyQt5.QtWidgets import QGridLayout, QSizePolicy
#pylint: enable=no-name-in-module

from datetime import timedelta

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
                    update_limits_on_value_change: bool = True):
        LinkableWidget.__init__(self, parent, link_manager, link_type)
        self._date_range_start = self._date_range_end = None
        self._interval = None
        self._update_limits_on_value_change = update_limits_on_value_change
        
        if paging:
            self._back_one = IconButton('left.svg', self.tr('Scroll Left'), self, QSize(8, 30))
            self._back_one.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self._back_one.clicked.connect(self._step(-1))
        self._from_selector = DateTimeEdit(self)
        self._to_selector = DateTimeEdit(self)
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

        self._from_selector.dateTimeChanged.connect(self._date_from_changed)
        self._to_selector.dateTimeChanged.connect(self._date_to_changed)

        self._menu = QMenu(self)
        self._reset = QAction(self.tr('Reset'), self)
        self._reset.triggered.connect(self._handle_reset)
        self._menu.addAction(self._reset)
        self._reset_enabled = reset_enabled

    dateFromChanged = pyqtSignal(QDateTime)
    dateToChanged = pyqtSignal(QDateTime)
    datesChanged = pyqtSignal(QDateTime, QDateTime)

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
            self.datesChanged.emit(self.dateFrom, self.dateTo)

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

    def _date_from_changed(self, value):
        if self._update_limits_on_value_change:
            self._to_selector.setMinimumDateTime(value)
        self.dateFromChanged.emit(value)

    def _date_to_changed(self, value):
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
