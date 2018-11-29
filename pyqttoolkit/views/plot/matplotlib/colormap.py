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
