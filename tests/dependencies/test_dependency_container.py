import pytest

from pyqttoolkit.dependencies import DependencyContainer, MissingDependency

@pytest.fixture
def container():
    return DependencyContainer()

class Foo:
    def __init__(self, bar):
        self._bar = bar
    
    @property
    def bar(self):
        return self._bar

class Baz:
    def __init__(self, bar, extra):
        self._bar = bar
        self._extra = extra
    
    @property
    def bar(self):
        return self._bar

    @property
    def extra(self):
        return self._extra

class Bar:
    def __init__(self, message):
        self._message = message
    
    @property
    def message(self):
        return self._message

def test_can_register_bar_instances(container):
    container.register_instance('bar', Bar('hello'))
    assert container.get_instance('bar').message == 'hello'

def test_can_resolve_foo_with_bar_instance(container):
    container.register_instance('bar', Bar('hello'))
    assert container.resolve(Foo).bar.message == 'hello'

def test_can_resolve_baz_with_registered_and_extras(container):
    container.register_instance('bar', Bar('hello'))
    baz = container.resolve(Baz, extras={'extra': 'world'})
    assert baz.bar.message == 'hello'
    assert baz.extra == 'world'

def test_raises_missing_dependency_exception_if_no_dependency_found(container):
    with pytest.raises(MissingDependency):
        container.resolve(Foo)