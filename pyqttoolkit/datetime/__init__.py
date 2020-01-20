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
from dateutil.parser import parse as parse_datetime

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
    if pd_timestamp is None:
        return QDateTime()
    return QDateTime(
        QDate(pd_timestamp.year, pd_timestamp.month, pd_timestamp.day),
        QTime(pd_timestamp.hour, pd_timestamp.minute, pd_timestamp.second, pd_timestamp.microsecond / 1000)
    )

def isoformat_to_datetime(isoformat: str):
    if isoformat is None:
        return None
    return parse_datetime(isoformat)

def round_timedelta(delta, resolution):
    if resolution is None:
        return delta
    days = delta.days - (delta.days % resolution.days) if resolution.days else delta.days
    seconds = delta.seconds - (delta.seconds % resolution.seconds) if resolution.seconds else delta.seconds
    return timedelta(days=days, seconds=seconds)

def round_datetime(time, resolution):
    if resolution is None:
        return time
    day = time.day - (time.day % resolution.days) if resolution.days else time.day
    hour = time.hour - (time.hour % resolution.seconds // 3600) if resolution.seconds // 3600 else time.hour
    minute = time.minute - (time.minute % ((resolution.seconds // 60) % 60)) if (resolution.seconds // 60) % 60 else time.minute
    second = time.second - (time.second % resolution.seconds) if resolution.seconds else time.second
    microsecond = time.microsecond - (time.microsecond % resolution.microseconds) if resolution.microseconds else time.microsecond
    return datetime(year=time.year, month=time.month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=time.tzinfo)

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

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + timedelta(days=iso_day-1, weeks=iso_week-1)
