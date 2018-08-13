#pylint: disable=no-name-in-module
from PyQt5.Qt import QObject, pyqtSignal
#pylint: enable=no-name-in-module

from .events import ModuleOpeningEvent

class ModuleBase(QObject):
    def __init__(self, id_, launcher_config=None):
        QObject.__init__(self)
        self._id = id_
        self._launcher_config = launcher_config
    
    opening = pyqtSignal(ModuleOpeningEvent)
    opened = pyqtSignal()

    @property
    def id(self):
        return self._id

    @property
    def launcher_config(self):
        return self._launcher_config
    
    @property
    def enabled(self):
        return True
    
    @property
    def is_root(self):
        return False

    def register(self, dependency_container):
        if self.enabled:
            self.register_dependencies(dependency_container)
            self.register_module(dependency_container.get_instance('module_service'))
            self.register_events(dependency_container.get_instance('event_registry'))
            self.register_converters(dependency_container.get_instance('object_converter'))
            self.register_metadata(dependency_container.get_instance('metadata_manager'))
    
    def register_module(self, module_service):
        module_service.register(self)
    
    def register_dependencies(self, dependency_container):
        pass
    
    def register_events(self, event_registry):
        pass
    
    def register_converters(self, object_converter):
        pass

    def register_metadata(self, metadata_manager):
        pass

    def handle_project_updated(self, project):
        pass

class Module(ModuleBase):
    def __init__(self, id_, model_type, view_type, view_manager_type, launcher_config=None):
        ModuleBase.__init__(self, id_, launcher_config)
        self._model_type = model_type
        self._view_type = view_type
        self._view_manager_type = view_manager_type
    
    @property
    def model_type(self):
        return self._model_type
    
    @property
    def view_type(self):
        return self._view_type
    
    @property
    def view_manager_type(self):
        return self._view_manager_type

class CompositeModule(QObject):
    def __init__(self, *modules):
        QObject.__init__(self)
        self._modules = modules
    
    def register(self, dependency_container):
        for module in self._modules:
            module.register(dependency_container)

class CommandModule(ModuleBase):
    def __init__(self, id_, launcher_config=None):
        ModuleBase.__init__(self, id_, launcher_config)
    
    def execute(self):
        raise NotImplementedError()
