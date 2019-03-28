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
class ScriptContext:
    def __init__(self, **kwargs):
        self._locals = kwargs
        self._result = {'value': None}
        self._output = ''
    
    @property
    def locals(self):
        return {**self._locals, 'result': self._result}
    
    @property
    def result(self):
        return self._result['value']
    
    @property
    def output(self):
        return self._output

    def add_output(self, value):
        self._output += value
