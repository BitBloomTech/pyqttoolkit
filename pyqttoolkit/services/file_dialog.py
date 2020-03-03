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
from os import path

#pylint: disable=no-name-in-module
from PyQt5.Qt import QStandardPaths, QFileDialog
#pylint: enable=no-name-in-module

class FileDialogService:
    def __init__(self, project_manager, application_configuration):
        self._project_manager = project_manager
        self._application_configuration = application_configuration
    
    def get_save_filename(self, parent, filter_, default_name=None):
        dialog = QFileDialog(parent, directory=self._get_default_directory(), filter=filter_)
        if default_name:
            dialog.selectFile(default_name)
        dialog.setModal(True)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec_() != QFileDialog.Accepted or not dialog.selectedFiles():
            return None
        return dialog.selectedFiles()[0]
    
    def get_open_filename(self, parent, filter_, file_mode=None):
        dialog = QFileDialog(parent, directory=self._get_default_directory(), filter=filter_)
        if file_mode:
            dialog.setFileMode(file_mode)
        if dialog.exec_():
            return dialog.selectedFiles()[0]
        else:
            return None
    
    def _get_default_directory(self):
        if not self._project_manager.filename:
            default_location = self._application_configuration.get_value('application.default_directory')
            if default_location and path.isdir(default_location):
                return default_location
            return QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        else:
            return path.dirname(self._project_manager.filename)
