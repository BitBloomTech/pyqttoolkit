from datetime import datetime, timedelta

#pylint: disable=no-name-in-module
from PyQt5.Qt import QDateTime, QDate, QTime
#pylint: enable=no-name-in-module

def q_datetime_to_datetime(q_datetime):
    return datetime(
        q_datetime.date().year(), q_datetime.date().month(), q_datetime.date().day(),
        q_datetime.time().hour(), q_datetime.time().minute(), q_datetime.time().second()
    )


def pd_timestamp_to_q_datetime(pd_timestamp):
    return QDateTime(
        QDate(pd_timestamp.year, pd_timestamp.month, pd_timestamp.day),
        QTime(pd_timestamp.hour, pd_timestamp.minute, pd_timestamp.second)
    )

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
    return datetime(year=time.year, month=time.month, day=day, hour=hour, minute=minute, second=0)

def step_qdatetime(control, fraction, interval, range_start, range_end):
    date_from = q_datetime_to_datetime(control.dateFrom)
    date_to = q_datetime_to_datetime(control.dateTo)
    range_start = q_datetime_to_datetime(range_start)
    range_end = q_datetime_to_datetime(range_end)
    delta = round_timedelta(((date_to - date_from) + interval) * fraction, interval)
    date_from = max(date_from + delta, range_start)
    date_to = min(date_to + delta, range_end)
    if date_to - date_from > timedelta(0):
        control.dateTo = QDateTime(date_to)
        control.dateFrom = QDateTime(date_from)
