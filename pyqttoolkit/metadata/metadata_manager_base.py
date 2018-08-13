class MetadataManagerBase:
    def __init__(self, project_manager):
        self._project_manager = project_manager
        self._types = {}

    def get_property(self, id_, property_):
        raise NotImplementedError()
    
    def set_property(self, id_, property_, value):
        raise NotImplementedError()
    
    def get_properties(self, id_, property_type):
        raise NotImplementedError()
    
    def add_properties(self, id_, property_type, properties=None):
        raise NotImplementedError()
    
    def delete_properties(self, id_, property_type):
        raise NotImplementedError()
    
    def get_metadata(self, property_type):
        raise NotImplementedError()
    
    def set_metadata(self, property_type, value):
        raise NotImplementedError()

    def _get_property_type_key(self, property_type):
        property_type_key = self._types.get(property_type)
        if not property_type_key:
            raise ValueError(f'Property type {property_type} not found')
        return property_type_key

    @property
    def metadata(self):
        return self._project_manager.project.metadata

    def register_type(self, type_, key):
        self._types[type_] = key
