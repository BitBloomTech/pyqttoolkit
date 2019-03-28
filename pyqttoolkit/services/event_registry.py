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
class EventTypes:
    application_closing = 'application_closing'
    opening_project = 'opening_project'
    importing_project = 'importing_project'
    save_requested = 'save_requested'
    close_project_requested = 'close_project_requested'

class FutureConnector:
    def __init__(self):
        self._handlers = []
    
    def connect(self, handler):
        self._handlers.append(handler)
    
    def register(self, event):
        for h in self._handlers:
            event.connect(h)

class EventRegistry:
    def __init__(self):
        self._events = {}
        self._future_events = {}
    
    def register(self, type_, event):
        self._events[type_] = event
        if type_ in self._future_events:
            self._future_events[type_].register(event)
    
    def event(self, type_):
        event = self._events.get(type_)
        if not event:
            return self._future_events.setdefault(type_, FutureConnector())
        else:
            return event
