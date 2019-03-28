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
from PyQt5.Qt import QWidget, QLineEdit, QHBoxLayout, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import auto_property

from . import ShrunkPushButton

class FileSelector(QWidget):
    def __init__(self, parent, filter_, file_dialog_service):
        QWidget.__init__(self, parent)
        self._file_dialog_service = file_dialog_service
        self._filter = filter_
        self._line_edit = QLineEdit(self)
        self._open_dialog = ShrunkPushButton('...', self)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._line_edit)
        self._layout.addWidget(self._open_dialog)
        self._line_edit.textChanged.connect(self.textChanged)
        self._open_dialog.clicked.connect(self._open_file_dialog)

    textChanged = pyqtSignal(str)

    @auto_property(str)
    def text(self):
        return self._line_edit.text()

    @text.setter
    def text(self, value):
        self._line_edit.setText(value)

    def _open_file_dialog(self):
        file_name = self._file_dialog_service.get_open_filename(self, self._filter)
        if file_name:
            self.text = file_name
