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
from pyqttoolkit.views.plot.matplotlib import MatPlotLibBase
from mpl_toolkits.axes_grid1 import Size, LocatableAxes

def _is_horizontal(position):
    return position == 'top' or position == 'bottom'


def _define_axes(position, cbar_size, _gap):
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


class MatPlotColorbar(MatPlotLibBase):
    def __init__(self, parent, file_dialog_service, cbar_height=0.2, v_gap=0.6, cbar_width=0.2, h_gap=0.6,
                 position='bottom', **kwargs):

        # First element of the tuple correspond to the nx_default or ny_default.
        # The second element is the nx and ny position for _colorbar_axes.
        self._nx = {'bottom': (1, 1), 'top': (1, 1), 'right': (1, 3), 'left': (4, 1)}
        self._ny = {'bottom': (3, 1), 'top': (1, 3), 'right': (1, 1), 'left': (1, 1)}

        super().__init__(parent,
                         file_dialog_service,
                         v_axes=[Size.Scaled(1.0)] if not _is_horizontal(position)
                         else _define_axes(position, cbar_height, v_gap),
                         h_axes=[Size.Scaled(1.0)] if _is_horizontal(position)
                         else _define_axes(position, cbar_width, h_gap),
                         nx_default=self._nx[position][0],
                         ny_default=self._ny[position][0], **kwargs)
        self._colorbar_axes = LocatableAxes(self._figure, self._divider.get_position())
        self._colorbar_axes.set_axes_locator(self._divider.new_locator(nx=self._nx[position][1], ny=self._ny[position][1]))
        self._figure.add_axes(self._colorbar_axes)
        self._cbar = None
        self._points = None
        self._position = position

    def _plot_colorbar(self, label):
        if self._cbar is None:
            self._cbar = self._figure.colorbar(self._points, self._colorbar_axes, orientation='horizontal' if
                                               _is_horizontal(self._position) else 'vertical')
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