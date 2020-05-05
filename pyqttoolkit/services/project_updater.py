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
from PyQt5.Qt import QObject, pyqtSignal, QTimer, QCoreApplication, QEvent, QSemaphore, QThread
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


class PropertyUpdatedEvent(QEvent):
    def __init__(self, prop):
        super().__init__(QEvent.User)
        self._prop = prop
    
    @property
    def prop(self):
        return self._prop

class UpdateCompleteEvent(QEvent):
    def __init__(self, handler, result):
        super().__init__(QEvent.User)
        self._handler = handler
        self._result = result
    
    def exec(self):
        self._handler(self._result)

class UpdateEvent(QEvent):
    def __init__(self, updater):
        super().__init__(QEvent.User)
        self._updater = updater
        self._result = None
        self._semaphore = QSemaphore(1)
        if QCoreApplication.instance().thread() != QThread.currentThread():
            self._semaphore.acquire()
    
    def exec(self):
        try:
            self._result = self._updater(None)
        finally:
            self._semaphore.release()
    
    def result(self):
        self._semaphore.acquire()
        return self._result

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
        result = update_function(None)
        if updated_properties:
            for prop in updated_properties:
                self._on_project_updated(prop)
        else:
            self._on_project_updated(None)
        if on_completed:
            QCoreApplication.postEvent(self, UpdateCompleteEvent(on_completed, result))
    
    def _on_project_updated(self, prop):
        QCoreApplication.postEvent(self, PropertyUpdatedEvent(prop))
    
    def event(self, event):
        if isinstance(event, PropertyUpdatedEvent):
            self.projectUpdated.emit(event.prop)
            return True
        if isinstance(event, UpdateCompleteEvent):
            event.exec()
            return True
        if isinstance(event, UpdateEvent):
            with self.update_lock:
                event.exec()
            return True
        return super().event(event)
