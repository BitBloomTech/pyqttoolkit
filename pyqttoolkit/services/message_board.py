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
from enum import Enum, IntEnum

#pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject, pyqtSignal
#pylint: enable=no-name-in-module

from ..properties import AutoProperty

class MessageType(Enum):
    validation_error = 0
    confirmation = 1
    application_exception = 2

class MessageResponse(IntEnum):
    ok = 1
    cancel = 2
    save = 4
    discard = 8
    ignore = 16

class MessageArgs(QObject):
    def __init__(self, parent, message_type, message, checkbox_message, response_type):
        QObject.__init__(self, parent)
        self._message_type = message_type
        self._message = message
        self._checkbox_message = checkbox_message
        self._response_type = response_type
        self._response = None
        self._checkbox_value = None
    
    @property
    def message_type(self):
        return self._message_type

    @property
    def message(self):
        return self._message
    
    @property
    def checkbox_message(self):
        return self._checkbox_message
    
    @property
    def response_type(self):
        return self._response_type
    
    @property
    def response(self):
        return self._response
    
    @response.setter
    def response(self, value):
        self._response = value
    
    @property
    def checkbox_value(self):
        return self._checkbox_value
    
    @checkbox_value.setter
    def checkbox_value(self, value):
        self._checkbox_value = value

class MessageBoard(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
    
    def post(self, message_type, message, response_type=MessageResponse.ok, checkbox_message=None):
        self.message = MessageArgs(self, message_type, message, checkbox_message, response_type)
        return self.message

    messageChanged = pyqtSignal(MessageArgs)

    message = AutoProperty(MessageArgs)
