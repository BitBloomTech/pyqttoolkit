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
