from pyqttoolkit.views.plot.matplotlib import MatPlotLibBase
from mpl_toolkits.axes_grid1 import Size, LocatableAxes

def is_horizontal(position):
    return position == 'top' or position == 'bottom'


def define_axes(position, cbar_size, _gap):
    if position == 'bottom':
        return [Size.Fixed(cbar_size), Size.Fixed(_gap), Size.Scaled(1.0)]
    elif position == 'top':
        return [Size.Scaled(1.0), Size.Fixed(_gap), Size.Fixed(cbar_size)]
    elif position == 'left':
        return [Size.Fixed(_gap/4), Size.Fixed(cbar_size), Size.Fixed(_gap*3), Size.Scaled(1.0)]
    elif position == 'right':
        return [Size.Scaled(1.0), Size.Fixed(_gap), Size.Fixed(cbar_size), Size.Fixed(_gap)]
    else:
        return None


# First element of the tuple correspond to the nx_default or ny_default.
# The second element is the nx and ny position for _colorbar_axes.
NX = {'bottom': (1, 1), 'top': (1, 1), 'right': (1, 3), 'left': (4, 1)}
NY = {'bottom': (3, 1), 'top': (1, 3), 'right': (1, 1), 'left': (1, 1)}


class MatPlotColorbar(MatPlotLibBase):
    def __init__(self, parent, file_dialog_service, cbar_height=0.2, v_gap=0.6, cbar_width=0.2, h_gap=0.6,
                 position='bottom', **kwargs):
        super().__init__(parent,
                         file_dialog_service,
                         v_axes=[Size.Scaled(1.0)] if not is_horizontal(position)
                         else define_axes(position, cbar_height, v_gap),
                         h_axes=[Size.Scaled(1.0)] if is_horizontal(position)
                         else define_axes(position, cbar_width, h_gap),
                         nx_default=NX[position][0],
                         ny_default=NY[position][0], **kwargs)
        self._colorbar_axes = LocatableAxes(self._figure, self._divider.get_position())
        self._colorbar_axes.set_axes_locator(self._divider.new_locator(nx=NX[position][1], ny=NY[position][1]))
        self._figure.add_axes(self._colorbar_axes)
        self._cbar = None
        self._points = None
        self._position = position

    def _plot_colorbar(self, label):
        if self._cbar is None:
            self._cbar = self._figure.colorbar(self._points, self._colorbar_axes, orientation='horizontal' if
                                               is_horizontal(self._position) else 'vertical')
            self._cbar.set_label(label)
        else:
            self._cbar.update_bruteforce(self._points)
            self._cbar.set_label(label)

    def _clear_colorbar(self):
        for a in self._colorbar_axes.collections:
            a.remove()

    @property
    def colorbar(self):
        return self._cbar

    @colorbar.setter
    def colorbar(self, cbar):
        self._cbar = cbar