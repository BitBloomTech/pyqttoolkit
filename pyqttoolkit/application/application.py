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
import sys
import logging

#pylint: disable=no-name-in-module
from PyQt5.Qt import QApplication, QWidget, pyqtSignal
#pyline: enable=no-name-in-module

from pyqttoolkit.services import MessageBoard, TaskRunner, ToolWindowService, EventRegistry, ObjectConverter
from pyqttoolkit.dependencies import DependencyContainer

LOGGER = logging.getLogger(__name__)

class Application(QApplication):
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self._dependency_container = DependencyContainer()

        self._module_service = None
        self._message_board = None
        self._project_manager = None

        self._handling_exception = False

        sys.excepthook = self._handle_exception
    
    mainWindowLoaded = pyqtSignal(QWidget)

    def run(self, filename=None):
        LOGGER.info('Running Application')
        self._register_default_services()
        self._register_modules()

        if filename:
            self._project_manager.load_project(filename)
        
        self.mainWindowLoaded.emit(self._module_service.openModule('Base'))
        return self.exec_()
    
    def notify(self, receiver, event):
        try:
            return QApplication.notify(self, receiver, event)
        #pylint: disable=broad-except
        except Exception as e:
            self._handle_exception(type(e), e, e.__traceback__)
            return True
    
    def _handle_exception(self, ex_type, ex_value, traceback_obj):
        LOGGER.error('Application Exception: %s, %s', ex_type, ex_value)
        if self._handling_exception:
            return
        self._handling_exception = True
        self._perform_exception_handling(ex_type, ex_value, traceback_obj)
        self._handling_exception = False
    
    def _perform_exception_handling(self, ex_type, ex_value, traceback_obj):
        pass
    
    def _register_default_services(self):
        self._dependency_container.register_instance('application', self)
        self._dependency_container.register_instance('dependency_container', self._dependency_container)
        self._dependency_container.register_instance('task_runner', TaskRunner(self))
        self._dependency_container.register_instance('message_board', MessageBoard(self))
        self._dependency_container.register_instance('tool_window_service', ToolWindowService(self._dependency_container))
        self._dependency_container.register_instance('event_registry', EventRegistry())
        self._dependency_container.register_instance('object_converter', ObjectConverter())
    
    def _register_modules(self):
        modules = self._get_modules()
        for module_type in [v for k, v in modules.__dict__.items() if k.endswith('Module')]:
            module = self._dependency_container.resolve(module_type)
            module.register(dependency_container=self._dependency_container)

        self._module_service = self._dependency_container.get_instance('module_service')

        self._message_board = self._dependency_container.get_instance('message_board')
        self._project_manager = self._dependency_container.get_instance('project_manager')
