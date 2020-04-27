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
""":mod:`datetime`
Defines the DateTimeEdit class
"""
from enum import Enum

#pylint: disable=no-name-in-module
from PyQt5.Qt import QDateTimeEdit, QDateTime, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import auto_property, AutoProperty

from .styleable import make_styleable

class DateTimeEdit(QDateTimeEdit):
    class Limit(Enum):
        min = 0
        max = 1

    def __init__(self, parent, default=Limit.min, calendar_popup=True):
        QDateTimeEdit.__init__(self, parent)
        self.setDisplayFormat('dd-MMM-yyyy hh:mm')
        self.setButtonSymbols(QDateTimeEdit.NoButtons)
        self._min_date = self._max_date = None
        self._start_date = self._end_date = None
        self.isLimit = False
        self._default = default
        self.isLimitChanged.connect(self._handle_is_limit_changed)
        self.dateTimeChanged.connect(self._handle_date_time_changed)
        self.setCalendarPopup(calendar_popup)

    valueChanged = pyqtSignal(QDateTime)
    isLimitChanged = pyqtSignal(bool)

    isLimit = AutoProperty(bool)
    
    def focusOutEvent(self, event):
        if self._start_date and self.dateTime() < self._start_date:
            self.setDateTime(self._start_date)
        elif self._min_date and self.dateTime() < self._min_date:
            self.setDateTime(self._min_date)
        elif self._end_date and self.dateTime() > self._end_date:
            self.setDateTime(self._end_date)
        elif self._max_date and self.dateTime() > self._max_date:
            self.setDateTime(self._max_date)
        return QDateTimeEdit.focusOutEvent(self, event)
    
    def setDateTimeRange(self, start_date, end_date):
        self._start_date = start_date
        self._end_date = end_date
    
    def setMinimumDateTime(self, min_date):
        self._min_date = min_date
    
    def setMaximumDateTime(self, max_date):
        self._max_date = max_date
    
    @auto_property(QDateTime)
    def value(self):
        return QDateTime() if self.isLimit else self.dateTime()

    @value.setter
    def value(self, value):
        value = value or QDateTime()
        if not value.isValid() and self._start_date is not None and self._end_date is not None:
            date_time = self._start_date if self._default == self.Limit.min else self._end_date
            is_limit = True
        else:
            date_time = value
            is_limit = False
        if self.dateTime() != date_time:
            self.setDateTime(date_time)
        self.isLimit = is_limit
        self.valueChanged.emit(value)

    def reset(self):
        self.value = QDateTime()
    
    def _handle_is_limit_changed(self, is_limit):
        stylesheet = 'DateTimeEdit {font: italic}' if is_limit else ''
        self.setStyleSheet(stylesheet)
    
    def _handle_date_time_changed(self, value):
        if value is not None or (isinstance(value, QDateTime) and value.isValid()):
            self.isLimit = False
        self.valueChanged.emit(self.value)


DateTimeEdit = make_styleable(DateTimeEdit)