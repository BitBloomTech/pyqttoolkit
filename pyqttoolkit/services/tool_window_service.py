
#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget
#pylint: enable=no-name-in-module

from pyqttoolkit.views import ToolWindow
from pyqttoolkit.viewmanagers import ToolViewManager

class ToolWindowService:
    def __init__(self, dependency_contianer):
        self._dependency_container = dependency_contianer
    
    def open(self, parent, model, name):
        view = self._dependency_container.resolve_for(type(model), QWidget, {'parent': None})
        if hasattr(model, 'showButtons'):
            show_buttons = model.showButtons
        else:
            show_buttons = True

        tool_window = ToolWindow(parent, view, name, show_buttons)
        view_manager = self._dependency_container.resolve_for(type(model), ToolViewManager, {'view': view, 'model': model})
        tool_window.accepted.connect(view_manager.save)
        tool_window.show()
