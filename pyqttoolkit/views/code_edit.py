#pylint: disable=no-name-in-module
from PyQt5.Qt import QTextEdit, QColor, Qt, QPalette, pyqtSignal, QFont, QTextOption
#pylint: enable=no-name-in-module

class CodeEdit(QTextEdit):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        self.document().setDefaultFont(QFont('Courier', pointSize=7))
        self.setWordWrapMode(QTextOption.NoWrap)
    
    editComplete = pyqtSignal(str)
    
    def setModel(self, model):
        self.setPlainText(model.text)
        model.textChanged.connect(self._set_text)
        self.editComplete.connect(self._handle_text_changed(model))
        model.validationMessageChanged.connect(self._handle_validation_message)
    
    def focusOutEvent(self, event):
        self.editComplete.emit(self.toPlainText())
        QTextEdit.focusOutEvent(self, event)
    
    def _set_text(self, text):
        if self.toPlainText() != text:
            self.setPlainText(text)

    def _handle_text_changed(self, model):
        def _setter(value):
            model.text = value
        return _setter

    def _handle_validation_message(self, message):
        if message:
            palette = self.palette()
            invalid_color = QColor(Qt.red)
            invalid_color.setAlphaF(0.2)
            palette.setColor(QPalette.Base, invalid_color)
        else:
            palette = self.style().standardPalette()
        self.setPalette(palette)
        self.setToolTip(message or None)
