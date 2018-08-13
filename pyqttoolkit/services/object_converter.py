class NoConverter(Exception):
    def __init__(self, type_):
        Exception.__init__(self, f'No converter for type {type_}')

class DictConverter:
    def to_dict(self, value):
        raise NotImplementedError()
    
    def from_dict(self, value):
        raise NotImplementedError()

class ObjectConverter:
    def __init__(self):
        self._converters = {}
    
    def register_converter(self, converter, value_type):
        self._converters.setdefault(value_type, []).append(converter)
    
    def to_dict(self, value):
        return self._get_converter(type(value), DictConverter).to_dict(value)
    
    def from_dict(self, value, value_type, **kwargs):
        return self._get_converter(value_type, DictConverter).from_dict(value, **kwargs)
    
    def _get_converter(self, value_type, converter_type):
        type_converters = [c for c in self._converters.get(value_type, []) if isinstance(c, converter_type)]
        if not type_converters:
            raise NoConverter(value_type)
        return type_converters[0]
