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
from collections import deque

class Cache:
    def __init__(self, size):
        self._storage = deque(maxlen=size)
    
    def __contains__(self, key):
        for k, v in self._storage:
            if k == key:
                return True
        return False

    def __getitem__(self, key):
        for k, v in self._storage:
            if k == key:
                return v
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        self._storage.append((key, value))

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        for k, v in self._storage:
            if k == key:
                self._storage.remove((key, v))
                return
    
    def delete_group(self, group):
        to_remove = []
        for k, v in self._storage:
            if k.startswith(group):
                to_remove.append((k, v))
        for v in to_remove:
            self._storage.remove(v)
            
    def setdefault(self, key, default_factory):
        if key in self:
            return self[key]
        value = default_factory()
        self[key] = value
        return value
    
    def clear(self):
        self._storage.clear()
