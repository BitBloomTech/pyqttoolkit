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
from PyQt5.Qt import QPalette, QColor, Qt, QObject
#pylint: enable=no-name-in-module

from pyqttoolkit.views import ModuleWindow
from . import MessageType
from ..colors import rgb_to_hex

class IncompatibleWidgets(Exception):
    def __init__(self):
        Exception.__init__(self)

class LinkManager(QObject):
    def __init__(self, parent, message_board, color_selection):
        QObject.__init__(self, parent)
        self._message_board = message_board
        self._current_widget = None
        self._color_count = 10
        self._selecting_color = (220/255, 240/255, 247/255)
        self._colors = color_selection.colors(self._color_count)
        self._link_count = 0
        self._link_groups = []
    
    def request_link(self, widget):
        if self._current_widget is None:
            self._current_widget = widget
            self._set_background_color(widget, self._selecting_color)
        elif self._current_widget == widget:
            current_group = self._current_link_group(widget)
            if current_group is not None:
                self._remove_widget_from_group(widget, current_group)
            self._set_background_color(widget, None)
            self._current_widget = None
        else:
            self._update_link(widget)
            self._current_widget = None
    
    def _update_link(self, widget):
        try:
            current_group = self._current_link_group(self._current_widget)
            if current_group is not None:
                if widget in current_group['widgets']:
                    self._remove_widget_from_group(widget, current_group)
                else:
                    self._add_widget_to_group(widget, current_group)
            else:
                other_group = self._current_link_group(widget)
                if other_group is not None:
                    self._add_widget_to_group(self._current_widget, other_group)
                else:
                    self._create_new_group(self._current_widget, widget)
        except IncompatibleWidgets:
            self._message_board.post(MessageType.validation_error, self.tr('It is not possible to link these controls'))
            self._set_background_color(self._current_widget, current_group and current_group['color'])
    
    def _current_link_group(self, widget):
        for group in self._link_groups:
            if widget in group['widgets']:
                return group
        return None

    def _create_new_group(self, from_widget, to_widget):
        from_widget.link(to_widget)
        group = {
            'widgets': [],
            'color': self._colors[self._link_count % self._color_count]
        }
        self._add_widget_to_group(from_widget, group, link=False)
        self._add_widget_to_group(to_widget, group, link=False)
        self._link_count += 1
        self._link_groups.append(group)
    
    def _add_widget_to_group(self, widget, group, link=True):
        existing_group = self._current_link_group(widget)
        if existing_group == group:
            return
        if existing_group is not None:
            self._remove_widget_from_group(widget, existing_group)
        if link:
            for w in group['widgets']:
                w.link(widget)
        group['widgets'].append(widget)
        self._get_module_window(widget).closing.connect(lambda _: self._remove_widget_from_group(widget, group))
        for w in group['widgets']:
            self._set_background_color(w, group['color'])
    
    def _remove_widget_from_group(self, widget, group):
        if group not in self._link_groups or widget not in group['widgets']:
            return
        group['widgets'].remove(widget)
        for w in group['widgets']:
            w.unlink(widget)
        self._set_background_color(widget, None)
        if len(group['widgets']) == 1:
            remaining_widget = group['widgets'][0]
            group['widgets'].remove(remaining_widget)
            self._link_groups.remove(group)
            self._set_background_color(remaining_widget, None)
        else:
            for w in group['widgets']:
                self._set_background_color(w, group['color'])

    def _get_module_window(self, widget):
        parent = widget.parent()
        while parent is not None:
            if isinstance(parent, ModuleWindow):
                return parent
            parent = parent.parent()

        raise ValueError('Could not find module window')

    def _set_background_color(self, widget, color):
        try:
            palette = widget.linkDisplay().palette()
            palette.setColor(QPalette.Background, QColor(rgb_to_hex(color)) if color is not None else Qt.transparent)
            widget.linkDisplay().setAutoFillBackground(True)
            widget.linkDisplay().setPalette(palette)
        except RuntimeError:
            # May have been deleted
            pass
