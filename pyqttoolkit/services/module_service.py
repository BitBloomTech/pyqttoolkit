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
""":mod:`module_service`
The module service, creates and manages qt widget modules
"""
from weakref import ref

#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSlot
#pylint: enable=no-name-in-module

from pyqttoolkit.modules import Module, CommandModule
from pyqttoolkit.views import ModuleWindow
from pyqttoolkit.modules.events import ModuleOpeningEvent

class ModuleService(QObject):
    """class::ModuleService
    This class creates and displays modules (views, models and view managers)
    """

    def __init__(self, dependency_container, theme_manager, project_updater, project_manager):
        QObject.__init__(self, None)
        self._theme_manager = theme_manager
        self._dependency_container = dependency_container
        self._view_manager_refs = {}
        self._window_refs = {}
        self._model_refs = {}
        self._view_managers = {}
        self._windows = {}
        self._models = {}
        self._registered_modules = {}
        self._project_updater = project_updater
        self._project_manager = project_manager
    
    def register(self, module):
        if module.id in self._registered_modules:
            raise ValueError('module')
        self._registered_modules[module.id] = module
        if module.launcher_config and self._project_updater is not None and self._project_manager is not None:
            self._project_updater.projectUpdated.connect(self._project_update_handler(module))
        
    def _project_update_handler(self, module):
        def _handler():
            module.handle_project_updated(self._project_manager.project)
        return _handler

    @pyqtSlot(str, QObject)
    def openModule(self, name):
        """function::openModule(self, name, parent, model)
        Opens the module with the specified name, setting the parent and model
        """
        if self._init_module(name):
            module = self._registered_modules[name]
            if isinstance(module, CommandModule):
                result = module.execute()
            elif isinstance(module, Module):
                result = self._create_module(name).show()
            else:
                raise ValueError('Invalid module type')
            self._module_opened(name)
            return result
        return None
    
    def closeModules(self):
        for id_, window in list(self._windows.items()):
            if id_ != 'root':
                window.close()
            
    def modules(self):
        return self._registered_modules
    
    def _init_module(self, id_):
        module = self._registered_modules[id_]
        opening_event = ModuleOpeningEvent()
        module.opening.emit(opening_event)
        return opening_event.accepted
    
    def _module_opened(self, id_):
        self._registered_modules[id_].opened.emit()
    
    def _create_module(self, id_):
        if not id_ in self._registered_modules:
            raise RuntimeError(f'Could not find module with id {id_}')
        if self._registered_modules[id_].is_root:
            return self._create_root_module(id_)
        else:
            return self._create_sub_module(id_)
    
    def _create_root_module(self, id_):
        window = self._dependency_container.resolve(self._registered_modules[id_].view_type)
        model = self._dependency_container.resolve(self._registered_modules[id_].model_type, {'parent': window})
        view_manager = self._registered_modules[id_].view_manager_type(window, model)
        self._windows['root'] = window
        self._models['root'] = model
        self._view_managers['root'] = view_manager
        return window

    def _create_sub_module(self, id_):
        window = ModuleWindow(self._theme_manager, id_)
        model = self._dependency_container.resolve(self._registered_modules[id_].model_type, {'parent': window})
        view = self._dependency_container.resolve(self._registered_modules[id_].view_type, {'parent': window})
        window.setModuleView(view)
        view_manager = self._registered_modules[id_].view_manager_type(view, model)

        self._view_managers[window.moduleId] = model
        self._windows[window.moduleId] = window
        self._models[window.moduleId] = model
        self._view_manager_refs[window.moduleId] = ref(view_manager)
        self._window_refs[window.moduleId] = ref(window)
        self._model_refs[window.moduleId] = ref(model)
        window.closing.connect(self._remove_module)
        return window

    def _remove_module(self, module_id):
        self._view_managers.pop(module_id)
        self._windows.pop(module_id).setParent(None)
        self._models.pop(module_id).setParent(None)
