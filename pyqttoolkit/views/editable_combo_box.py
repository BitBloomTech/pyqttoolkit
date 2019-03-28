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
""":mod:`editable_combo_box`
Defines the EditableComboBox class
"""
#pylint: disable=no-name-in-module
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QComboBox
#pylint: enable=no-name-in-module

class EditableComboBox(QComboBox):
    """class::EditableComboBox
    A combo box that is editable by default, and adds the current item if focus is lost
    """
    def __init__(self, parent):
        QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.installEventFilter(self)

    def eventFilter(self, _obj, event):
        """function::eventFilter(self, _obj, evet)
        Override the QComboBox.eventFilter method to provide lost focus functionality
        """
        if event.type() == QEvent.FocusOut and self.currentText():
            index = self.findText(self.currentText())
            if index == -1:
                self.addItem(self.currentText())
                index = self.findText(self.currentText())
                self.setCurrentIndex(index)
            self.activated.emit(index)
        return QComboBox.eventFilter(self, _obj, event)
