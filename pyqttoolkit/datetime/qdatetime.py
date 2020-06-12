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
from datetime import datetime, timedelta
from .datetime import round_timedelta

import pandas as pd

#pylint: disable=no-name-in-module
from PyQt5.Qt import QDateTime, QDate, QTime
#pylint: enable=no-name-in-module

def q_datetime_to_datetime(q_datetime: QDateTime):
    if q_datetime is None or not q_datetime.isValid():
        return None

    return datetime(
        q_datetime.date().year(), q_datetime.date().month(), q_datetime.date().day(),
        q_datetime.time().hour(), q_datetime.time().minute(), q_datetime.time().second(),
        q_datetime.time().msec() * 1000
    )


def pd_timestamp_to_q_datetime(pd_timestamp: datetime):
    if pd_timestamp is None or pd.isna(pd_timestamp):
        return QDateTime()
    return QDateTime(
        QDate(pd_timestamp.year, pd_timestamp.month, pd_timestamp.day),
        QTime(pd_timestamp.hour, pd_timestamp.minute, pd_timestamp.second, pd_timestamp.microsecond / 1000)
    )

def step_qdatetime(control, fraction, interval, range_start, range_end):
    date_from = q_datetime_to_datetime(control.dateFrom)
    date_to = q_datetime_to_datetime(control.dateTo)
    range_start = q_datetime_to_datetime(range_start)
    range_end = q_datetime_to_datetime(range_end)
    delta = round_timedelta((date_to - date_from) * fraction, interval)
    date_from = max(date_from + delta, range_start)
    date_to = min(date_to + delta, range_end)
    if date_to - date_from > timedelta(0):
        control.dateTo = QDateTime(date_to)
        control.dateFrom = QDateTime(date_from)
