
#pylint: disable=no-name-in-module
from PyQt5.Qt import QWidget
#pylint: enable=no-name-in-module

from pyqttoolkit.views import ToolWindow
from pyqttoolkit.viewmanagers import ToolViewManager

class ToolWindowService:
    def __init__(self, dependency_contianer):
        self._dependency_container = dependency_contianer
        self._active_tools = []
    
    def open(self, parent, model, name):
        view = self._dependency_container.resolve_for(type(model), QWidget, {'parent': None})
        if hasattr(model, 'showButtons'):
            show_buttons = model.showButtons
        else:
            show_buttons = True

        tool_window = ToolWindow(parent, view, name, show_buttons)
        view_manager = self._dependency_container.resolve_for(type(model), ToolViewManager, {'view': view, 'model': model})
        tool_window.accepted.connect(self._tool_window_accepted(tool_window, view_manager))
        self._active_tools.append((tool_window, view_manager))
        tool_window.show()

    def _tool_window_accepted(self, tool_window, view_manager):
        def _handler():
            view_manager.save()
            self._active_tools.remove((tool_window, view_manager))
        return _handler