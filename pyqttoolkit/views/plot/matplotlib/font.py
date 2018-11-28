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
