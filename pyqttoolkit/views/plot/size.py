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
from mpl_toolkits.axes_grid1 import Size

class ToggleableFixed(Size._Base):
    def __init__(self, size):
        self._size = size
        self._active = False

    def activate(self):
        self._active = True
    
    def deactivate(self):
        self._active = False

    def get_size(self, _renderer):
        return 0.0, self._size if self._active else 0.0

class MaxWidth(Size.MaxWidth):
    def remove_artist(self, artist):
        if artist in self._artist_list:
            self._artist_list.remove(artist)
    
    def get_size(self, renderer):
        if self._artist_list:
            return Size.MaxWidth.get_size(self, renderer)
        return 0, 0
