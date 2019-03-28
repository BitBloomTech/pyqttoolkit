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
from PyQt5.Qt import QDialog, QDialogButtonBox, QGridLayout
#pylint: enable=no-name-in-module

class ToolWindow(QDialog):
    def __init__(self, parent, view, name, show_buttons=True):
        QDialog.__init__(self, parent)
        self.setWindowTitle(name)

        view.setParent(self)

        self._layout = QGridLayout(self)
        self._layout.addWidget(view, 0, 0)

        if show_buttons:
            self._buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
            self._buttons.accepted.connect(self.accept)
            self._buttons.rejected.connect(self.reject)
            self._layout.addWidget(self._buttons, 1, 0)
        
        self.setLayout(self._layout)
