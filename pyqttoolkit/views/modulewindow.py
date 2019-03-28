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
""":mod:`modulewindow`
Module window widget
"""
from uuid import uuid4

#pylint: disable=no-name-in-module
from PyQt5.Qt import pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.modules.events import RejectableEvent

from .main_window import MainWindow

class ModuleWindow(MainWindow):
    """class::ModuleWindow
    Class for use with QWidget-based modules
    """
    def __init__(self, theme_manager, title=None):
        MainWindow.__init__(self, None, theme_manager)
        self._id = uuid4()
        self._theme_manager = theme_manager
        if title:
            self.setWindowTitle(title)

    closing = pyqtSignal(str)

    def setModuleView(self, module_view):
        """function::setModuleView(self, module_view)
        Sets the module view (central widget)
        """
        self.setCentralWidget(module_view)

    @property
    def moduleId(self):
        """function::id(self)
        Returns the id for this module window
        """
        return str(self._id)

    def closeEvent(self, event):
        """function::closeEvent(self, event)
        Decorates the base class with a closing event
        """
        if hasattr(self.centralWidget(), 'prepareClose'):
            close_event = RejectableEvent()
            self.centralWidget().prepareClose(close_event)
            if not close_event.accepted:
                event.ignore()
                return
        MainWindow.closeEvent(self, event)
        if event.isAccepted():
            self.centralWidget().close()
            self.closing.emit(self.moduleId)

    @property
    def themeManager(self):
        return self._theme_manager
