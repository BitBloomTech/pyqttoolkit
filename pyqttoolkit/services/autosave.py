#pylint: disable=no-name-in-module
from PyQt5.QtCore import QTimer, QObject
#pylint: enable=no-name-in-module


class Autosave(QObject):
    def __init__(self, save_function, filename, interval=30000):
        QObject.__init__(self)
        self._save_function = save_function
        self._timer = QTimer()
        self._interval = interval
        self._timer.timeout.connect(self._save)
        self._filename = filename
    
    @property
    def filename(self):
        return self._filename
    
    def start(self):
        self._timer.start(self._interval)
    
    def stop(self):
        self._timer.stop()
    
    def _save(self):
        self._save_function(self._filename)
