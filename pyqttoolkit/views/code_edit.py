#pylint: disable=no-name-in-module
from PyQt5.Qt import Qt, QWidget, QGridLayout, QTextEdit, QColor, Qt, QPalette, pyqtSignal, QFont, QTextOption, QSplitter, QTextBrowser, QLabel
#pylint: enable=no-name-in-module

class CodeTextEdit(QTextEdit):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        self.document().setDefaultFont(QFont('Courier', pointSize=7))
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setTabStopWidth(32)

    editComplete = pyqtSignal(str)

    def focusOutEvent(self, event):
        self.editComplete.emit(self.toPlainText())
        QTextEdit.focusOutEvent(self, event)

class CodeEdit(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._text_edit = CodeTextEdit(self)
        self._output_pane = QTextBrowser(self)
        self._output_pane.document().setDefaultFont(QFont('Courier', pointSize=7))
        self._output_pane.setWordWrapMode(QTextOption.NoWrap)

        self._output_pane_container = QWidget(self)
        self._output_pane_layout = QGridLayout(self._output_pane_container)
        self._output_pane_layout.setContentsMargins(0, 16, 0, 0)
        self._output_pane_layout.addWidget(QLabel(self.tr('Script Output')), 0, 0)
        self._output_pane_layout.addWidget(self._output_pane)

        self._splitter = QSplitter(Qt.Vertical, self)

        self._splitter.addWidget(self._text_edit)
        self._splitter.addWidget(self._output_pane_container)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 1)

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._splitter, 0, 0)

        self._text_edit.editComplete.connect(self.editComplete)
    
    editComplete = pyqtSignal(str)

    @property
    def textEdit(self):
        return self._text_edit
    
    @property
    def outputPane(self):
        return self._output_pane
    
    def setFontSize(self, font_size):
        self._text_edit.document().setDefaultFont(QFont('Courier', pointSize=font_size))
        self._output_pane.document().setDefaultFont(QFont('Courier', pointSize=font_size))
        self._text_edit.setTabStopWidth(font_size * 2)
        self._output_pane.setTabStopWidth(font_size * 2)

    def setModel(self, model):
        self._text_edit.setPlainText(model.text)
        self._output_pane.setPlainText(model.output)
        model.textChanged.connect(self._set_text(self._text_edit))
        model.outputChanged.connect(self._set_text(self._output_pane, True))
        self.editComplete.connect(self._handle_text_changed(model))
        model.validationMessageChanged.connect(self._handle_validation_message)
    
    def _set_text(self, widget, scroll_to_end=False):
        def _(text):
            if widget.toPlainText() != text:
                widget.setPlainText(text)
                if scroll_to_end:
                    widget.verticalScrollBar().setSliderPosition(widget.verticalScrollBar().maximum())
        return _

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
        self._text_edit.setPalette(palette)
        self._text_edit.setToolTip(message or None)
