class EventTypes:
    application_closing = 'application_closing'
    opening_project = 'opening_project'
    importing_project = 'importing_project'
    save_requested = 'save_requested'
    close_project_requested = 'close_project_requested'

class FutureConnector:
    def __init__(self):
        self._handlers = []
    
    def connect(self, handler):
        self._handlers.append(handler)
    
    def register(self, event):
        for h in self._handlers:
            event.connect(h)

class EventRegistry:
    def __init__(self):
        self._events = {}
        self._future_events = {}
    
    def register(self, type_, event):
        self._events[type_] = event
        if type_ in self._future_events:
            self._future_events[type_].register(event)
    
    def event(self, type_):
        event = self._events.get(type_)
        if not event:
            return self._future_events.setdefault(type_, FutureConnector())
        else:
            return event
