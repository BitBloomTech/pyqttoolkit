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
from PyQt5.Qt import (
    Qt, QWidget, QGridLayout, QPlainTextEdit, QColor,
    QPalette, pyqtSignal, QFont, QTextOption, QSplitter,
    QTextBrowser, QLabel, QSize, QRect, QPainter,
    QFontMetrics, QPointF, QTextEdit, QTextFormat,
    QEvent
)
#pylint: enable=no-name-in-module

from .python_syntax import PythonHighlighter

class LineNumberArea(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self._editor = editor
    
    def sizeHint(self):
        return QSize(self._editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self._editor.lineNumberAreaPaintEvent(event)

class CodeTextEdit(QPlainTextEdit):
    def __init__(self, parent):
        QPlainTextEdit.__init__(self, parent)
        self.document().setDefaultFont(QFont('Courier', pointSize=7))
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setTabStopWidth(32)

        self._line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

        self._key_press_rules = None

    editComplete = pyqtSignal(str)

    def focusInEvent(self, event):
        result = QPlainTextEdit.focusInEvent(self, event)
        self.highlightCurrentLine()
        return result
        
    def focusOutEvent(self, event):
        self.editComplete.emit(self.toPlainText())
        result = QPlainTextEdit.focusOutEvent(self, event)
        self.highlightCurrentLine()
        return result
    
    def lineNumberAreaWidth(self):
        digits = 1
        block_count = max(1, self.blockCount())
        while block_count >= 10:
            block_count /= 10
            digits += 1
        
        space = 3 + self.fontMetrics().width('9') * digits

        return space
    
    def fontMetrics(self):
        return QFontMetrics(self.document().defaultFont())
    
    def updateLineNumberAreaWidth(self, block_count):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)

        contents_rect = self.contentsRect()
        self._line_number_area.setGeometry(QRect(contents_rect.left(), contents_rect.top(), self.lineNumberAreaWidth(), contents_rect.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)
        painter.setFont(self.document().defaultFont())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self._line_number_area.width(), self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlightCurrentLine(self):
        extra_selections = []
        if self.hasFocus() and not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(Qt.yellow).lighter(180)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def setKeyPressRules(self, rules):
        self._key_press_rules = rules

    def keyPressEvent(self, event):
        if event and self._key_press_rules:
            next_text = self._key_press_rules.getText(event.key())
            if next_text:
                self.insertPlainText(next_text)
                return
        QPlainTextEdit.keyPressEvent(self, event)

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
        model.textChanged.connect(self._set_text(self._text_edit))
        if hasattr(model, 'output'):
            self._output_pane.setPlainText(model.output)
            model.outputChanged.connect(self._set_text(self._output_pane, True))
            self._output_pane.setVisible(True)
        else:
            self._output_pane_container.setVisible(False)
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

class PythonCodeEdit(CodeEdit):
    def __init__(self, parent):
        CodeEdit.__init__(self, parent)
        self._highlighter = PythonHighlighter(self.textEdit.document())
        self.textEdit.setKeyPressRules(PythonKeyPressRules(self.textEdit, 4))

class KeyPressRules:
    def getText(self, key):
        raise NotImplementedError()

class PythonKeyPressRules(KeyPressRules):
    def __init__(self, text_edit, tab_width):
        self._text_edit = text_edit
        self._tab_width = tab_width

    def getText(self, key):
        if key in [Qt.Key_Tab, Qt.Key_Backtab]:
            return ' ' * self._tab_width
        if key in [Qt.Key_Return, Qt.Key_Enter]:
            current_position = self._text_edit.textCursor().positionInBlock()
            current_line = self._text_edit.textCursor().block().text()
            if current_position == len(current_line):
                if current_line.strip() and current_line.strip()[-1] == ':':
                    return '\n' + ' ' * self._tab_width
                n_spaces = 0
                for c in current_line:
                    if c == ' ':
                        n_spaces += 1
                    else:
                        break
                return '\n' + ' ' * n_spaces
        return None
            