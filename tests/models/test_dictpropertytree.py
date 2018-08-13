from enum import Enum
import pytest
#pylint: disable=no-name-in-module
from PyQt5.Qt import Qt, QAbstractItemModel, pyqtSignal, QModelIndex, QVariant
#pylint: enable=no-name-in-module

from pyqttoolkit.models import DictPropertyTreeModel

class FooBarProperties(Enum):
    foo = 0
    baz = 1

class FooBarPropertyTree(DictPropertyTreeModel):
    def __init__(self, parent, data):
        DictPropertyTreeModel.__init__(self, parent, data)
    
    @property
    def propertyTypes(self):
        return {
            FooBarProperties.foo: str,
            FooBarProperties.baz: int
        }

@pytest.mark.parametrize('data,result',[
    ({}, 2),
    ({'foo': 'bar'}, 2),
    ({'foo': 'bar', 'baz': 42}, 2),
    ({'foo': 'bar', 'baz': {}}, 2),
])
def test_row_count_returns_correct_row_count_for_dict(data, result):
    assert FooBarPropertyTree(None, data).rowCount(QModelIndex()) == result

@pytest.mark.parametrize('data,result',[
    ({'foo': 'bar'}, 0),
])
def test_row_count_returns_correct_row_count_for_child(data, result):
    model = FooBarPropertyTree(None, data)
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == result

def test_parent_of_child_is_identity():
    model = FooBarPropertyTree(None, {'foo': 'bar'})
    index = model.index(0, 0, QModelIndex())
    child = model.index(0, 0, index)
    assert child.parent() == index
