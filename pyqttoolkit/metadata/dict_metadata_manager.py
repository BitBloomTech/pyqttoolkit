from enum import Enum
from copy import deepcopy

from .metadata_manager_base import MetadataManagerBase

class DictMetadataManager(MetadataManagerBase):
    def __init__(self, application):
        MetadataManagerBase.__init__(self, application)

    def get_property(self, id_, property_):
        if not isinstance(property_, Enum):
            raise TypeError('Property must be enum type')
        return deepcopy(self.metadata.get(self._get_property_type_key(type(property_)), {}).get(id_, {}).get(property_.name, None))
    
    def set_property(self, id_, property_, value):
        if not isinstance(property_, Enum):
            raise TypeError('Property must be enum type')
        if id_ is None:
            raise ValueError('Must specify an ID')
        property_type = type(property_)
        property_type_key = self._get_property_type_key(property_type)
        self.metadata.setdefault(property_type_key, {}).setdefault(id_, self.default_properties(property_type))[property_.name] = value
    
    def get_properties(self, id_, property_type):
        return deepcopy(self.metadata.get(self._types.get(property_type), {}).get(id_, None))
    
    def add_properties(self, id_, property_type, properties=None):
        if id_ is None:
            raise ValueError('Must specify an ID')
        self.metadata.setdefault(self._get_property_type_key(property_type), {}).setdefault(id_, properties or self.default_properties(property_type))
    
    def delete_properties(self, id_, property_type):
        if id_ is None:
            raise ValueError('Must specify an ID')
        metadata = self.metadata.get(self._get_property_type_key(property_type), {})
        if id_ in metadata:
            del metadata[id_]
    
    def get_metadata(self, property_type):
        return deepcopy(self.metadata.get(self._get_property_type_key(property_type)))
    
    def set_metadata(self, property_type, value):
        self.metadata[self._get_property_type_key(property_type)] = deepcopy(value)

    @staticmethod
    def default_properties(property_type):
        return {p.name: None for p in property_type}
