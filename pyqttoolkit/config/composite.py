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
from .base import BaseApplicationConfiguration

class CompositeApplicationConfiguration(BaseApplicationConfiguration):
    def __init__(self, *inners):
        self._inners = inners
    
    def get_value(self, key):
        for inner in self._inners:
            value = inner.get_value(key)
            if value:
                return value
        return None
    
    def set_value(self, key, value):
        self._inners[0].set_value(key, value)
