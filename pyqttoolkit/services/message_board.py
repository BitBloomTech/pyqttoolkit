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

class MessageArgs(QObject):
    def __init__(self, parent, message_type, message, response_type):
        QObject.__init__(self, parent)
        self._message_type = message_type
        self._message = message
        self._response_type = response_type
        self._response = None
    
    @property
    def message_type(self):
        return self._message_type

    @property
    def message(self):
        return self._message
    
    @property
    def response_type(self):
        return self._response_type
    
    @property
    def response(self):
        return self._response
    
    @response.setter
    def response(self, value):
        self._response = value

class MessageBoard(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
    
    def post(self, message_type, message, response_type=MessageResponse.ok):
        self.message = MessageArgs(self, message_type, message, response_type)
        return self.message

    messageChanged = pyqtSignal(MessageArgs)

    message = AutoProperty(MessageArgs)
