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
from matplotlib import rcParams
from matplotlib.font_manager import findfont, FontProperties
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

class MatPlotLibFont:
    def __init__(self, font):
        font_file = findfont(FontProperties(family=font))
        self._is_ttf = font_file.endswith('.ttf')
        if not self._is_ttf:
            raise ValueError('Unknown font type')
        self._font = TTFont(font_file)

    def get_size(self, text, pointsize, dpi):
        return self._get_ttf_size(text, pointsize, dpi)
    
    def _get_ttf_size(self, text, pointsize, dpi):
        cmap = self._font['cmap']
        t = cmap.getcmap(3,1).cmap
        s = self._font.getGlyphSet()
        width = 0
        for c in text:
            if ord(c) in t and t[ord(c)] in s:
                char = s[t[ord(c)]]
            else:
                char = s['.notdef']
            width += char.width
        units_per_em = self._font['head'].unitsPerEm
        return self._convert_to_pixels(width, pointsize, dpi, units_per_em), self._convert_to_pixels(units_per_em, pointsize, dpi, units_per_em)
    
    def _convert_to_pixels(self, value, pointsize, dpi, units_per_em):
        value_pts = value * float(pointsize) / units_per_em
        value_in = value_pts / 72
        value_pixels = value_in * dpi
        return value_pixels

    @staticmethod
    def default():
        return MatPlotLibFont(rcParams['font.family'])
