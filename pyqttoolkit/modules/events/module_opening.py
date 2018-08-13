from .rejectable import RejectableEvent

class ModuleOpeningEvent(RejectableEvent):
    def __init__(self):
        RejectableEvent.__init__(self)
