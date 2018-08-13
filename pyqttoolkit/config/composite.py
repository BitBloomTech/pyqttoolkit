from .base import BaseApplicationConfiguration

class CompositeApplicationConfiguration(BaseApplicationConfiguration):
    def __init__(self, *inners):
        self._inners = inners
    
    def get_value(self, key):
        for inner in self._inners:
            value = inner.get_value(key)
            if value:
                return value
        return None
    
    def set_value(self, key, value):
        self._inners[0].set_value(key, value)
