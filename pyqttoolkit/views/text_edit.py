#pylint: disable=no-name-in-module
from PyQt5.Qt import QTextEdit, pyqtSignal, QFont
#pylint: enable=no-name-in-module

class TextEdit(QTextEdit):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        self.document().setDefaultFont(QFont('Courier', pointSize=7))
    
    editComplete = pyqtSignal(str)
    
    def focusOutEvent(self, event):
        self.editComplete.emit(self.toPlainText())
        QTextEdit.focusOutEvent(self, event)
