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
import inspect

class MissingDependency(Exception):
    def __init__(self, object_type, dependency_name):
        Exception.__init__(self, object_type, dependency_name)

class DependencyContainer:
    def __init__(self):
        self._instances = {}
        self._types = {}

    def register_instance(self, name, value):
        self._instances[name] = value
    
    def register_type(self, type_for, base_type, result_type):
        self._types.setdefault(type_for, {})[base_type] = result_type

    def get_instance(self, name):
        return self._instances[name]

    def resolve(self, type_, extras=None, none_for_missing=False):
        args = self._get_args(type_)
        all_dependencies = {**self._instances, **(extras or {})}
        for a in args:
            if a not in all_dependencies.keys():
                if none_for_missing:
                    all_dependencies[a] = None
                else:
                    raise MissingDependency(type_, a)
        return type_(**{a: all_dependencies[a] for a in args})
    
    def resolve_for(self, type_for, base_type, extras=None):
        type_to_resolve = self._types[type_for][base_type]
        return self.resolve(type_to_resolve, extras)
    
    @staticmethod
    def _get_args(type_):
        return inspect.signature(type_).parameters
