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
from PyQt5.QtCore import QTimer, QObject
#pylint: enable=no-name-in-module


class Autosave(QObject):
    def __init__(self, save_function, filename, interval=30000):
        QObject.__init__(self)
        self._save_function = save_function
        self._timer = QTimer()
        self._interval = interval
        self._timer.timeout.connect(self._save)
        self._filename = filename
    
    @property
    def filename(self):
        return self._filename
    
    def start(self):
        self._timer.start(self._interval)
    
    def stop(self):
        self._timer.stop()
    
    def _save(self):
        self._save_function(self._filename)
