# pyqttoolkit
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
""":mod:`toolkit`
Defines various utils useful in views
"""
import logging
from math import isnan
from weakref import ref, WeakKeyDictionary

from pyqttoolkit.logs import TRACE

LOGGER = logging.getLogger(__name__)

def updater(obj, name):
    """function::updater(obj, name)
    Higher order function which returns a function to update the property
    specified by name in the object specified by obj
    """
    def _update_value(value):
        setattr(obj, name, value)
    return _update_value

def one_way_bind(src, dest, src_name, dest_name=None):
    """function::one_way_bind(src, dest, src_name, [dest_name])
    Propagate changes in src to dest, and set dest to value of src
    """
    dest_name = dest_name or src_name
    src_signal = getattr(type(src), AutoProperty.get_notify_property_name(src_name))
    dest_prop = getattr(type(dest), dest_name)
    src_signal.__get__(src, type(src)).connect(dest_prop.updater(dest))
    src_value = getattr(src, src_name)
    setattr(dest, dest_name, src_value)
    return updater

def bind(src, dest, src_name, dest_name=None, two_way=True):
    """function::bind(src, dest, src_name, [dest_name[, two_way]])
    Propagate changes in src to dest, and set dest to value of src
    Optionally bind dest to src
    """
    dest_name = dest_name or src_name
    one_way_bind(src, dest, src_name, dest_name)
    if two_way:
        one_way_bind(dest, src, dest_name, src_name)

def one_way_unbind(src, dest, src_name, dest_name=None):
    dest_name = dest_name or src_name
    src_signal = getattr(type(src), AutoProperty.get_notify_property_name(src_name))
    dest_prop = getattr(type(dest), dest_name)
    src_signal.__get__(src, type(src)).disconnect(dest_prop.updater(dest))

def unbind(src, dest, src_name, dest_name=None, two_way=True):
    dest_name = dest_name or src_name
    one_way_unbind(src, dest, src_name, dest_name)
    if two_way:
        one_way_unbind(dest, src, dest_name, src_name)

def auto_property(type_, *args, **kwargs):
    """function::auto_property(type, *args, **kwargs)
    Decorator function for AutoProperty, creates an AutoProperty with the given getter
    """
    def _(fget):
        return AutoProperty(type_=type_, fget=fget, *args, **kwargs)
    return _

def values_equal(left, right):
    return left == right or (isinstance(left, float) and isinstance(right, float) and isnan(left) and isnan(right))

def connect_all(handler, *signals):
    for signal in signals:
        signal.connect(handler)

def disconnect_all(handler, *signals):
    for signal in signals:
        signal.disconnect(handler)

#pylint: disable=too-many-arguments
class AutoProperty:
    """class::AutoProperty
    Descriptor which provides property and signal functionality to objects
    """
    native_types = [list, str, int, float, bool]
    def __init__(self, type_, fget=None, fset=None, fdel=None, default_value=None, notify=None):
        self._type = type_
        self._default_value = default_value
        self._notify = notify
        self._name = None
        self._fget = fget
        self._fset = fset
        self._fdel = fdel
        self._updaters = WeakKeyDictionary()
        self._notify_depth = 0
        self._max_notify_depth = 5

    def __set_name__(self, obj, name):
        self._name = name
        if not self._notify and self._has_notify_property(obj):
            self._notify = self._get_notify_property(obj)

    def __get__(self, obj, type_=None):
        if obj is None:
            return self
        if not self._name:
            raise ValueError('Cannot get property, name has not been set!')
        if self._uses_delegates():
            if not self._fget:
                raise ValueError(f'No getter provided for property {self._name}')
            return self._fget(obj)
        elif self._name not in obj.__dict__:
            return self._default_value
        else:
            return obj.__dict__[self._name]

    def __set__(self, obj, value):
        if obj is None:
            return
        if not self._name:
            raise ValueError('Cannot set property, name has not been set!')
        if not self._uses_delegates() and not self._notify:
            raise ValueError(f'Cannot set property {self._name}, unable to notify!')
        if value is not None and self._type and not isinstance(value, self._type):
            value_type = type(value)
            raise ValueError(
                f'Invalid type {value_type} provided for property {self._name}: '
                f'must be of type {self._type}'
            )
        if self._uses_delegates():
            if not self._fset:
                raise ValueError(f'No setter provided for property {self._name}')
            self._fset(obj, value)
        elif self._name not in obj.__dict__ or not values_equal(obj.__dict__[self._name], value):
            LOGGER.log(TRACE, 'Setting %s.%s to %s', obj, self._name, value)
            obj.__dict__[self._name] = value
            if self._notify_depth == self._max_notify_depth:
                LOGGER.error('Maximum notify depth exceeded for %s.%s', obj, self._name)
            if self._notify and self._notify_depth <= self._max_notify_depth:
                self._notify_depth += 1
                LOGGER.log(TRACE, 'Notifying change of %s.%s to %s', obj, self._name, value)
                self._notify.__get__(obj, type(obj)).emit(value)
                self._notify_depth -= 1

    def __delete__(self, obj):
        if not self._name:
            raise ValueError('Cannot delete property, name has not been set!')
        if self._uses_delegates():
            if not self._fdel:
                raise ValueError(f'No deleter provided for property {self._name}')
            self._fdel(obj)
        else:
            del obj.__dict__[self._name]

    def updater(self, obj, outer_value=None):
        """function::updater(self, obj, outer_value=None)
        Returns a function that can be used to update with the specified outer_value
        If outer_value is not specified, updates with the inner_value passed to the inner function
        """
        if not obj in self._updaters:
            obj_ref = ref(obj)
            def _(inner_value=None):
                self.__set__(obj_ref(), outer_value or inner_value)
            self._updaters[obj] = _
        return self._updaters[obj]

    def getter(self, fget):
        """function::getter(self, fget)
        Function decorator to create a getter
        Returns a copy of this AutoProperty with fget as the getter
        """
        return type(self)(
            self._type, fget, self._fset, self._fdel,
            self._default_value, self._notify
        )

    def setter(self, fset):
        """function::setter(self, fset)
        Function decorator to create a setter
        Returns a copy of this AutoProperty with fset as the setter
        """
        return type(self)(
            self._type, self._fget, fset, self._fdel,
            self._default_value, self._notify
        )

    def deleter(self, fdel):
        """function::deleter(self, fdel)
        Function decorator to create a deleter
        Returns a copy of this AutoProperty with fdel as the deleter
        """
        return type(self)(
            self._type, self._fget, self._fset, fdel,
            self._default_value, self._notify
        )

    def _get_notify_property(self, obj):
        return getattr(obj, self.get_notify_property_name(self._name))

    def _has_notify_property(self, obj):
        return hasattr(obj, self.get_notify_property_name(self._name))

    def _uses_delegates(self):
        return self._fget or self._fset or self._fdel

    @staticmethod
    def get_notify_property_name(name):
        """function::get_notify_property_name(name)
        Returns the name of the notify property
        """
        return f'{name}Changed'
