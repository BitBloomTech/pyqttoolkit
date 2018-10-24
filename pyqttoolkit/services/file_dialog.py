from os import path

#pylint: disable=no-name-in-module
from PyQt5.Qt import QStandardPaths, QFileDialog
#pylint: enable=no-name-in-module

class FileDialogService:
    def __init__(self, project_manager):
        self._project_manager = project_manager
    
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
            return QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        else:
            return path.dirname(self._project_manager.filename)
