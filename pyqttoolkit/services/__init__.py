""":mod:`services`
Defines classes and functions that provide services to the models of the application
"""
from .task_runner import TaskRunner
from .message_board import MessageBoard, MessageArgs, MessageType, MessageResponse
from .module_service import ModuleService
from .tool_window_service import ToolWindowService
from .link_manager import LinkManager, IncompatibleWidgets
from .email import EmailService
from .event_registry import EventRegistry, EventTypes
from .object_converter import ObjectConverter, DictConverter
from .autosave import Autosave
from .hotkey_manager import HotkeyManager, HotkeyEvents
from .theme_manager import ThemeManager
from .project_updater import ProjectUpdater
from .file_dialog import FileDialogService
