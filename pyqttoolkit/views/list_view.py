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
from PyQt5.Qt import QListView, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class ListView(QListView):
    def __init__(self, parent):
        QListView.__init__(self, parent)
        self.selectedIndexChanged.connect(self._handle_selected_index_changed)
        self._updating_selection = False
    
    selectedItemsChanged = pyqtSignal()
    selectedIndexChanged = pyqtSignal(int)

    selectedIndex = AutoProperty(int)
    
    def selectionChanged(self, current_selection, previous_selection):
        self._updating_selection = True
        result = QListView.selectionChanged(self, current_selection, previous_selection)
        self.selectedIndex = current_selection.indexes()[0].row() if current_selection.indexes() else -1
        self.selectedItemsChanged.emit()
        self._updating_selection = False
        return result

    def _handle_selected_index_changed(self, index):
        if self.model() is not None and not self._updating_selection:
            self.setCurrentIndex(self.model().createIndex(index, 0))
