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
