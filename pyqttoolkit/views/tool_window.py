#pylint: disable=no-name-in-module
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
