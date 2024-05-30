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
import pandas as pd

def calculate_interval(values, sort=True):
    if len(values) < 2:
        return None
    values_series = pd.Series(values)
    if sort:
        values_series = values_series.sort_values()
    # We want to ensure that the calculated interval is accurate for 90% of values to avoid mistakenly losing values
    return (values_series - values_series.shift(1)).quantile(0.1)
