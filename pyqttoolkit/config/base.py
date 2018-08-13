class BaseApplicationConfiguration:
    def get_value(self, key):
        raise NotImplementedError()
    
    def set_value(self, key, value):
        raise NotImplementedError()
