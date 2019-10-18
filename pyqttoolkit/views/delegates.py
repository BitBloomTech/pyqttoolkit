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
from enum import Enum

#pylint: disable=no-name-in-module
from PyQt5.Qt import QStyledItemDelegate, QTableView, QTreeView, QStringListModel, QStyle, QStyleOptionViewItem
#pylint: enable=no-name-in-module

from pyqttoolkit.models.roles import DataRole, EditorAuxDataRole
from pyqttoolkit.views import BindableComboBox, DateTimeEdit, BulkValueSelectorWidget, Popup, make_styleable

class ComboBoxItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
    
    def setComboBoxModel(self, model):
        self._combo_box_model = model

    def createEditor(self, parent, option, index):
        combo_box = BindableComboBox(parent)
        combo_box.setModel(self._combo_box_model)
        combo_box.move(parent.pos())
        value = self.parent().model().data(index, DataRole)
        if isinstance(self.parent(), QTableView):
            combo_box.setFixedWidth(self.parent().columnWidth(index.column()) * self.parent().columnSpan(index.row(), index.column()))
            combo_box.setFixedHeight(self.parent().rowHeight(index.row()) * self.parent().rowSpan(index.row(), index.column()))
        else:
            combo_box.setFixedWidth(self.parent().columnWidth(index.column()))
            combo_box.setFixedHeight(self.parent().rowHeight(index))
        if isinstance(value, Enum):
            value = value.name
        combo_box.value = value
        combo_box.currentIndexChanged.connect(self.closeEditor(combo_box))
        return combo_box
    
    def setEditorData(self, editor, index):
        editor.showPopup()

    def closeEditor(self, control):
        def _handler():
            self.parent().commitData(control)
            self.parent().closeEditor(control, QStyledItemDelegate.NoHint)
        return _handler

class DateTimeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        editor = DateTimeEdit(parent)
        editor.setDate(self.parent().model().data(index, DataRole))
        return editor

class BulkValueSelectorItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        editor = BulkValueSelectorWidget(parent)
        editor.setFixedHeight(int(self.parent().height() * 0.8))
        editor.setFixedWidth(200)
        editor.values = QStringListModel(self.parent().model().data(index, EditorAuxDataRole), self)
        editor.selectedValues = self.parent().model().data(index, DataRole)
        popup = Popup(parent, editor)
        editor.dataCommitted.connect(self.closePopup(popup))
        return popup
    
    def setEditorData(self, editor, index):
        editor.popupAtPosition(self.parent(), self.parent().visualRect(index))
    
    def setModelData(self, editor, model, index):
        model.setData(index, sorted(editor.contents.selectedValues))

    def closePopup(self, popup):
        def _handler(selected_values):
            self.parent().closeEditor(popup, QStyledItemDelegate.NoHint)
        return _handler
