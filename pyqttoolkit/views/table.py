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
""":mod:`synthesis`
Defines the SynthesisView class
"""
#pylint: disable=no-name-in-module
from PyQt5.Qt import QTableView, QKeySequence, QApplication, QMenu, QAction, Qt
#pylint: enable=no-name-in-module

class TableView(QTableView):
    def __init__(self, parent):
        QTableView.__init__(self, parent)
        self._menu = QMenu(self)
        self._copy_action = QAction(self.tr('Copy'), self)
        self._copy_action.triggered.connect(self.copy)
        self._copy_action.setShortcuts(QKeySequence.Copy)
        self._copy_with_headers_action = QAction(self.tr('Copy With Headers'), self)
        self._copy_with_headers_action.triggered.connect(self.copyWithHeaders)
        self._paste_action = QAction(self.tr('Paste'), self)
        self._paste_action.triggered.connect(self.paste)
        self._paste_action.setShortcuts(QKeySequence.Paste)
        self._menu.addAction(self._copy_action)
        self._menu.addAction(self._copy_with_headers_action)
        self._menu.addAction(self._paste_action)
        self.addAction(self._copy_action)
        self.addAction(self._copy_with_headers_action)
        self.addAction(self._paste_action)
    
    @property
    def pasteEnabled(self):
        return self._paste_action.isEnabled()
    
    @pasteEnabled.setter
    def pasteEnabled(self, value):
        self._paste_action.setEnabled(value)

    @property
    def copyEnabled(self):
        return self._copy_action.isEnabled()
    
    @copyEnabled.setter
    def copyEnabled(self, value):
        self._copy_action.setEnabled(value)
    
    def setModel(self, model):
        QTableView.setModel(self, model)
        if model:
            model.setParent(self)
    
    def copy(self):
        self._do_copy()
    
    def copyWithHeaders(self):
        self._do_copy(include_headers=True)
    
    def _do_copy(self, include_headers=False):
        indexes = self._get_selected_indexes()
        current_row = None
        paste_data = ''
        columns = []
        columns_added = []
        row_header_added = False
        for i in indexes:
            if include_headers and i.column() not in columns_added:
                columns.append(self.model().headerData(i.column(), Qt.Horizontal) or '')
                columns_added.append(i.column())
            if current_row is not None:
                if i.row() != current_row:
                    paste_data += '\n'
                    row_header_added = False
                else:
                    paste_data += '\t'
            if include_headers and not row_header_added:
                paste_data += (self.model().headerData(i.row(), Qt.Vertical) or '') + '\t'
                row_header_added = True
            data = self.model().data(i)
            paste_data += str(data) if data is not None else ''
            current_row = i.row()
        if include_headers:
            header_row = '\t' + '\t'.join(columns) + '\n'
            paste_data = header_row + paste_data
        QApplication.clipboard().setText(paste_data)
    
    def paste(self):
        value = QApplication.clipboard().text()
        rows = value.strip('\n').split('\n')
        selected_indexes = self._get_selected_indexes()
        if selected_indexes:
            start_row = selected_indexes[0].row()
            start_column = selected_indexes[0].column()
        else:
            start_row = start_column = 0
        indexes = []
        if hasattr(self.model(), 'beginPaste'):
            self.model().beginPaste()
        for row_id, row_text in zip(range(len(rows)), rows):
            cells = row_text.split('\t')
            for col_id, cell_text in zip(range(len(cells)), cells):
                index = self.model().createIndex(row_id + start_row, col_id + start_column)
                self.model().setData(index, cell_text)
                indexes.append(index)
        if hasattr(self.model(), 'endPaste'):
            self.model().endPaste(indexes[0], indexes[-1])

    def _get_selected_indexes(self):
        return list(sorted(sorted(self.selectedIndexes(), key=lambda i: i.column()), key=lambda i: i.row()))

    def contextMenuEvent(self, event):
        self._menu.exec_(event.globalPos())
