from .rejectable import RejectableEvent

class AddSignalEvent(RejectableEvent):
    def __init__(self, signal_id, signal_type):
        RejectableEvent.__init__(self)
        self._signal_id = signal_id
        self._signal_type = signal_type
    
    @property
    def signal_id(self):
        return self._signal_id
    
    @property
    def signal_type(self):
        return self._signal_type
