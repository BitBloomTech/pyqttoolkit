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
from PyQt5.Qt import Qt
#pylint: enable=no-name-in-module

class HotkeyEvents(Enum):
    next_instance_y = 0
    previous_instance_y = 1
    next_instance_x = 2
    previous_instance_x = 3
    next_t = 4
    previous_t = 5
    zoom_in = 6
    zoom_out = 7

class HotkeyManager:
    keymap = {
        Qt.Key_0: '0',
        Qt.Key_1: '1',
        Qt.Key_2: '2',
        Qt.Key_3: '3',
        Qt.Key_4: '4',
        Qt.Key_5: '5',
        Qt.Key_6: '6',
        Qt.Key_7: '7',
        Qt.Key_8: '8',
        Qt.Key_9: '9',
        Qt.Key_A: 'a',
        Qt.Key_B: 'b',
        Qt.Key_C: 'c',
        Qt.Key_D: 'd',
        Qt.Key_E: 'e',
        Qt.Key_F: 'f',
        Qt.Key_G: 'g',
        Qt.Key_H: 'h',
        Qt.Key_I: 'i',
        Qt.Key_J: 'j',
        Qt.Key_K: 'k',
        Qt.Key_L: 'l',
        Qt.Key_M: 'm',
        Qt.Key_N: 'n',
        Qt.Key_O: 'o',
        Qt.Key_P: 'p',
        Qt.Key_Q: 'q',
        Qt.Key_R: 'r',
        Qt.Key_S: 's',
        Qt.Key_T: 't',
        Qt.Key_U: 'u',
        Qt.Key_V: 'v',
        Qt.Key_W: 'w',
        Qt.Key_X: 'x',
        Qt.Key_Y: 'y',
        Qt.Key_Z: 'z',
        Qt.Key_BraceLeft: '{',
        Qt.Key_BraceRight: '}',
        Qt.Key_BracketLeft: '[',
        Qt.Key_BracketRight: ']',
        Qt.Key_Colon: ':',
        Qt.Key_Semicolon: ';',
        Qt.Key_Greater: '>',
        Qt.Key_Less: '<',
        Qt.Key_Comma: ',',
        Qt.Key_Period: '.',
        Qt.Key_Space: '<space>',
        Qt.Key_Up: '<up>',
        Qt.Key_Down: '<down>',
        Qt.Key_Left: '<left>',
        Qt.Key_Right: '<right>',
        Qt.Key_Backslash: '\\',
    }

    defaults = {
        HotkeyEvents.next_instance_y: 'w',
        HotkeyEvents.previous_instance_y: 's',
        HotkeyEvents.next_instance_x: 'shift+w',
        HotkeyEvents.previous_instance_x: 'shift+s',
        HotkeyEvents.next_t: 'd',
        HotkeyEvents.previous_t: 'a',
        HotkeyEvents.zoom_in: 'e',
        HotkeyEvents.zoom_out: 'q'
    }

    def __init__(self, application_configuration):
        self._application_configuration = application_configuration
        self._cached_configuration = self._get_configuration()

    def get_default_keystring(self, event):
        return self.defaults[event]

    def keyevent_to_string(self, event):
        key = self.keymap.get(event.key())
        if not key:
            return None
        modifiers = []
        if Qt.ShiftModifier & event.modifiers():
            modifiers.append('shift')
        if Qt.ControlModifier & event.modifiers():
            modifiers.append('control')
        if Qt.AltModifier & event.modifiers():
            modifiers.append('alt')
        return '+'.join(modifiers + [key])

    def assign_keystring(self, event, keystring):
        path = f'application.hotkeys.{event.name}'
        self._application_configuration.set_value(path, keystring)
        self._cached_configuration = self._get_configuration()
    
    def get_keystring(self, event):
        return self._cached_configuration.get(event.name) or self.get_default_keystring(event)

    def handle_event(self, event, handlers):
        keystring = self.keyevent_to_string(event)
        if not keystring:
            return False
        for hotkey_event in HotkeyEvents:
            if self.get_keystring(hotkey_event) == keystring and handlers.get(hotkey_event):
                handlers.get(hotkey_event)()
                return True
        return False

    def _get_configuration(self):
        return self._application_configuration.get_value('application.hotkeys') or {}
