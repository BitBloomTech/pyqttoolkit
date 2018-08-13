from datetime import datetime, timedelta
from pyqttoolkit.datetime import round_datetime

def test_round_to_nearest_10_min_succeeds():
    dt = datetime(2018, 3, 23, 12, 12, 12)
    res = timedelta(seconds=60 * 10)
    assert round_datetime(dt, res) == datetime(2018, 3, 23, 12, 10, 0)