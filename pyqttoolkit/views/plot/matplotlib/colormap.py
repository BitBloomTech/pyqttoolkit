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
from matplotlib.colors import LinearSegmentedColormap

class MatPlotLibColormap:
    def __init__(self, colormap, limits=None, invert=False):
        self._colormap = colormap.reversed() if colormap and invert else colormap
        self._limits = limits

    @property
    def colormap(self):
        return self._colormap
    
    @property
    def has_limits(self):
        return self._limits is not None
    
    @property
    def limits(self):
        return self._limits
    
    @staticmethod
    def from_list(values, invert=False):
        if all(len(v) == 3 for v in values):
            return MatPlotLibColormap(LinearSegmentedColormap.from_list('cmap', values), invert=invert)
        if not all(len(v) == 2 for v in values):
            return MatPlotLibColormap(None)
        values = sorted(values, key=lambda v: v[0])
        range_lower, range_upper = values[0][0], values[-1][0]
        if range_lower == 0.0 and range_upper == 1.0:
            return MatPlotLibColormap(LinearSegmentedColormap.from_list('cmap', values), invert=invert)
        total_range = range_upper - range_lower
        values = [((p - range_lower) / total_range, c) for p, c in values]
        return MatPlotLibColormap(LinearSegmentedColormap.from_list('cmap', values), limits=(range_lower, range_upper), invert=invert)
