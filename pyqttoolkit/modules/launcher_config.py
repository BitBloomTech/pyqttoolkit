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
from PyQt5.Qt import QObject, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class LauncherConfig(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.enabled = False
        self.checked = False

    enabledChanged = pyqtSignal(bool)
    checkedChanged = pyqtSignal(bool)

    enabled = AutoProperty(bool)
    checked = AutoProperty(bool)
    
    @property
    def buttonTitle(self):
        return None
    
    @property
    def menuTitle(self):
        return None

    @property
    def buttonIcon(self):
        return None
    
    @property
    def menu(self):
        return None
    
    @property
    def order(self):
        return 0

    @property
    def alwaysEnabled(self):
        return False
