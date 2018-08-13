from enum import Enum
import pytest
import pandas as pd

from pyqttoolkit.metadata import DictMetadataManager
from pyqttoolkit.metadata import DataframeMetadataManager

class FooProperties(Enum):
    bar = 0
    baz = 1
    bam = 2

class MetadataProject:
    def __init__(self):
        self._metadata = {}

    @property
    def metadata(self):
        return self._metadata

class ProjectProvider:
    def __init__(self, project):
        self._project = project

    @property
    def project(self):
        return self._project

@pytest.fixture(params=['dataframe', 'dict'])
def metadata_manager(request):
    if request.param == 'dict':
        return DictMetadataManager(ProjectProvider(MetadataProject()))
    if request.param == 'dataframe':
        return DataframeMetadataManager(ProjectProvider(MetadataProject()))

def test_get_property_raises_value_error_if_property_type_not_registered(metadata_manager):
    with pytest.raises(ValueError):
        metadata_manager.get_property('id', FooProperties.bar)

def test_get_property_returns_none_if_no_value(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    assert metadata_manager.get_property('id', FooProperties.bar) is None

@pytest.mark.parametrize('value', [42, '42'])
def test_get_property_returns_set_property_value(metadata_manager, value):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.set_property('id', FooProperties.bar, value)
    assert metadata_manager.get_property('id', FooProperties.bar) == value

def test_get_properties_returns_none_before_values_set(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    assert metadata_manager.get_properties('id', FooProperties) is None

def test_get_properties_returns_default_values(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.set_property('id', FooProperties.bar, 42)
    assert metadata_manager.get_properties('id', FooProperties) == {'bar': 42, 'baz': None, 'bam': None}

def test_add_properties_adds_default_properties(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.add_properties('id', FooProperties)
    assert metadata_manager.get_properties('id', FooProperties) == {'bar': None, 'baz': None, 'bam': None}

def test_add_properties_add_specified_default_properties(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    default_properties = {'bar': 42, 'baz': 'hello', 'bam': None}
    metadata_manager.add_properties('id', FooProperties, default_properties)
    assert metadata_manager.get_properties('id', FooProperties) == default_properties

def test_delete_properties_removes_properties(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.add_properties('id', FooProperties)
    assert metadata_manager.get_properties('id', FooProperties) == {'bar': None, 'baz': None, 'bam': None}
    metadata_manager.delete_properties('id', FooProperties)
    assert metadata_manager.get_properties('id', FooProperties) is None

def test_get_metadata_returns_all_metadata(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.add_properties('id_1', FooProperties)
    metadata_manager.add_properties('id_2', FooProperties)
    assert metadata_manager.get_metadata(FooProperties) == {
        'id_1': {'bar': None, 'baz': None, 'bam': None},
        'id_2': {'bar': None, 'baz': None, 'bam': None},
    }

def test_set_metadata_sets_properties_correctly(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.set_metadata(FooProperties, {
        'id_1': {'bar': 42, 'baz': 'hello', 'bam': None},
        'id_2': {'bar': 24, 'baz': 'world', 'bam': 'not none'},
    })
    assert metadata_manager.get_property('id_1', FooProperties.bar) == 42
    assert metadata_manager.get_property('id_1', FooProperties.baz) == 'hello'
    assert metadata_manager.get_property('id_1', FooProperties.bam) is None
    assert metadata_manager.get_property('id_2', FooProperties.bar) == 24
    assert metadata_manager.get_property('id_2', FooProperties.baz) == 'world'
    assert metadata_manager.get_property('id_2', FooProperties.bam) == 'not none'

def test_can_set_and_get_tuple(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')

    metadata_manager.set_property('id', FooProperties.bar, (1, 2))
    assert metadata_manager.get_property('id', FooProperties.bar) == (1, 2)

def test_add_properties_doesnt_override_existing(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.set_property('id', FooProperties.bar, (1, 2))

    metadata_manager.add_properties('id', FooProperties)

    assert metadata_manager.get_property('id', FooProperties.bar) == (1, 2)

def test_can_store_list_of_values(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    metadata_manager.set_property('id', FooProperties.bar, [1, 2, 3, 4, 5, 6])

    assert metadata_manager.get_property('id', FooProperties.bar) == [1, 2, 3, 4, 5, 6]
    
def test_can_store_list_of_dicts(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    values = [{'foo': i} for i in range(10)]
    metadata_manager.set_property('id', FooProperties.bar, values)

    assert metadata_manager.get_property('id', FooProperties.bar) == values

def test_can_store_dict(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    value = {'foo': 42}
    metadata_manager.set_property('id', FooProperties.bar, value)

    assert metadata_manager.get_property('id', FooProperties.bar) == value

def test_add_new_column_sets_all_values_to_default(metadata_manager):
    metadata_manager.register_type(FooProperties, 'foo_properties')
    existing = {
        'id-1': {
            'bar': 42,
            'baz': 24
        },
        'id-2': {
            'bar': 42,
            'baz': 24
        }
    }
    metadata_manager.set_metadata(FooProperties, existing)
    metadata_manager.set_property('id-1', FooProperties.bam, 'hello')
    assert metadata_manager.get_property('id-2', FooProperties.bam) is None