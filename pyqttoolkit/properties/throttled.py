import time
from inspect import signature

#pylint: disable=no-name-in-module
from PyQt5.QtCore import QTimer
#pylint: enable=no-name-in-module

def arg_count(f):
    return len(signature(f).parameters)

class ThrottledBoundSignal:
    def __init__(self, *types, interval=100):
        self._types = types
        self._interval = interval
        self._functions = []
        self._timer = None
        self._last_event_time = 0
        self._current_values = None
    
    def emit(self, *values):
        self._current_values = values
        time_since_last_event = time.clock() - self._last_event_time
        if self._timer is None and time_since_last_event >= (self._interval / 1000):
            self._emit_now()
            return
        if self._timer is None:
            self._timer = QTimer()
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self._emit_now)
            self._timer.start(self._interval)

    def _emit_now(self):
        for f in self._functions:
            f(*self._current_values[:arg_count(f)])
        self._last_event_time = time.clock()
        self._current_values = None
        self._timer = None
    
    def connect(self, f):
        self._functions.append(f)

    def disconnect(self, f):
        self._functions.remove(f)

class ThrottledSignal:
    def __init__(self, *types, interval=1000):
        self._name = None
        self._types = types
        self._interval = interval
    
    def __set_name__(self, obj, name):
        self._name = name
    
    def __get__(self, obj, type_=None):
        if obj is None:
            return self
        if not self._name:
            raise ValueError('Cannot get property, name has not been set!')
        if self._name not in obj.__dict__:
            obj.__dict__[self._name] = ThrottledBoundSignal(*self._types, interval=self._interval)
        return obj.__dict__[self._name]
