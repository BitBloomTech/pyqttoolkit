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
""":mod:`project_updater`
Defines the ProjectUpdater class, which enables the project to be updated
"""
import inspect
from threading import Lock

#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSignal
#pylint: enable=no-name-in-module

def _check_attribute(name, fields, project):
    if not name in fields:
        raise ValueError(f'Could not access property {name} of project {type(project)}')


class ProjectProxy:
    _storage = {}

    def __init__(self, project):
        ProjectProxy._storage[self] = {}
        ProjectProxy._storage[self]['_fields'] = []
        for name, obj in inspect.getmembers(type(project)):
            if inspect.isdatadescriptor(obj):
                ProjectProxy._storage[self]['_fields'].append(name)
        ProjectProxy._storage[self]['_updates'] = {}
        ProjectProxy._storage[self]['_project'] = project
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del ProjectProxy._storage[self]

    def __setattr__(self, name, value):
        _check_attribute(name, ProjectProxy._storage[self]['_fields'], ProjectProxy._storage[self]['_project'])
        ProjectProxy._storage[self]['_updates'][name] = value

    def __getattribute__(self, name):
        if name == 'updates':
            return ProjectProxy._storage[self]['_updates']
        _check_attribute(name, ProjectProxy._storage[self]['_fields'], ProjectProxy._storage[self]['_project'])
        return getattr(ProjectProxy._storage[self]['_project'], name)


class ProjectUpdater(QObject):
    """class::ProjectUpdater
    Allows the project to be updated
    """
    def __init__(self, project_manager):
        QObject.__init__(self, project_manager)
        self._project_manager = project_manager
        self._is_dirty = False
        self._lock = Lock()

    projectUpdated = pyqtSignal(str)

    @property
    def dirty(self):
        return self._is_dirty

    @dirty.setter
    def dirty(self, value):
        self._is_dirty = value
    
    @property
    def update_lock(self):
        return self._lock

    def update_project(self, update_function, updated_properties=None, on_completed=None):
        """function::update_project(self, update_function)
        Calls the update_function to perform the desired updates
        """
        self.dirty = True
        result = None
        with ProjectProxy(self._project_manager.project) as proxy:
            with self.update_lock:
                result = update_function(proxy)
            for name, value in proxy.updates.items():
                setattr(self._project_manager.project, name, value)
                self.projectUpdated.emit(name)
            for prop in set(updated_properties or []) - set(proxy.updates.keys()):
                self.projectUpdated.emit(prop)
            if not proxy.updates and updated_properties is None:
                self.projectUpdated.emit(None)
        if on_completed:
            on_completed(result)
