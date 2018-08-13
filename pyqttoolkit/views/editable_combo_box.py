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
