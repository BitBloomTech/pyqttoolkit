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
from .rejectable import RejectableEvent

class AddSignalEvent(RejectableEvent):
    def __init__(self, signal_id, signal_type):
        RejectableEvent.__init__(self)
        self._signal_id = signal_id
        self._signal_type = signal_type
    
    @property
    def signal_id(self):
        return self._signal_id
    
    @property
    def signal_type(self):
        return self._signal_type
