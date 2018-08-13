""":mod:`datetime`
Defines the DateTimeEdit class
"""
#pylint: disable=no-name-in-module
from PyQt5.Qt import QDateTimeEdit
#pylint: enable=no-name-in-module

class DateTimeEdit(QDateTimeEdit):
    def __init__(self, parent):
        QDateTimeEdit.__init__(self, parent)
        self.setDisplayFormat('dd-MMM-yy hh:mm')
        self.setButtonSymbols(QDateTimeEdit.NoButtons)
        self._min_date = self._max_date = None
        self._start_date = self._end_date = None
    
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
