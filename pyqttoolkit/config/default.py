from .base import BaseApplicationConfiguration

class DefaultApplicationConfiguration(BaseApplicationConfiguration):
    def __init__(self, config):
        self._configuration = config
    
    def get_value(self, key):
        return self._configuration.get(key)

    def set_value(self, key, value):
        self._configuration[key] = value
