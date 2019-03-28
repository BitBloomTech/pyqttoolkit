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
from datetime import datetime

from jinja2 import Environment

class ScriptTemplate:
    def __init__(self, template_string, name):
        self._template_string = template_string
        self._template_name = name
    
    def render(self, *args, **kwargs):
        environment = Environment()
        environment.globals.update(**self._get_globals())
        template = environment.from_string(self._template_string)
        return template.render(*args, **kwargs)
    
    def _get_globals(self):
        return {
            'zip': zip,
            'len': len,
            'template_name': self._template_name,
            'now': datetime.now().strftime('%Y-%m-%d %I:%M'),
            'indent': self._indent
        }
    
    def _indent(self, level):
        return '    ' * level
