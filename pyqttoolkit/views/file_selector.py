#pylint: disable=no-name-in-module
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
