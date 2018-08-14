import inspect

class MissingDependency(Exception):
    def __init__(self, object_type, dependency_name):
        Exception.__init__(self, object_type, dependency_name)

class DependencyContainer:
    def __init__(self):
        self._instances = {}
        self._types = {}

    def register_instance(self, name, value):
        self._instances[name] = value
    
    def register_type(self, type_for, base_type, result_type):
        self._types.setdefault(type_for, {})[base_type] = result_type

    def get_instance(self, name):
        return self._instances[name]

    def resolve(self, type_, extras=None):
        args = self._get_args(type_)
        all_dependencies = {**self._instances, **(extras or {})}
        for a in args:
            if not a in all_dependencies.keys():
                raise MissingDependency(type_, a)
        return type_(**{a: all_dependencies[a] for a in args})
    
    def resolve_for(self, type_for, base_type, extras=None):
        type_to_resolve = self._types[type_for][base_type]
        return self.resolve(type_to_resolve, extras)
    
    @staticmethod
    def _get_args(type_):
        return inspect.signature(type_).parameters
