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
from enum import Enum
from copy import deepcopy
import json

import pandas as pd

from .metadata_manager_base import MetadataManagerBase

class DataframeMetadataManager(MetadataManagerBase):
    def __init__(self, project_manager):
        MetadataManagerBase.__init__(self, project_manager)

    def get_property(self, id_, property_):
        if not isinstance(property_, Enum):
            raise TypeError('Property must be enum type')
        property_type = type(property_)
        property_type_key = self._get_property_type_key(property_type)
        if property_type_key not in self.metadata:
            return None
        if id_ not in self.metadata[property_type_key].index:
            return None
        if property_.name not in self.metadata[property_type_key].columns:
            return None
        value_read = deepcopy(self.metadata[property_type_key].loc[id_, property_.name])
        if isinstance(value_read, str) and value_read.startswith('json:'):
            return json.loads(value_read.replace('json:', ''))
        return value_read
        
    def set_property(self, id_, property_, value):
        if not isinstance(property_, Enum):
            raise TypeError('Property must be enum type')
        if id_ is None:
            raise ValueError('Must specify an ID')
        property_type = type(property_)
        property_type_key = self._get_property_type_key(property_type)
        if not property_type_key in self.metadata:
            self.metadata[property_type_key] = pd.DataFrame(columns=self.columns(property_type))
        if not id_ in self.metadata[property_type_key].index:
            self.metadata[property_type_key].loc[id_, :] = None
        if not property_.name in self.metadata[property_type_key].columns:
            self.metadata[property_type_key].loc[:, property_.name] = None
        self.metadata[property_type_key].loc[id_, property_.name] = self._get_value_to_store(value)
    
    def get_properties(self, id_, property_type):
        property_type_key = self._get_property_type_key(property_type)
        if property_type_key not in self.metadata:
            return None
        if id_ not in self.metadata[property_type_key].index:
            return None
        return self.metadata[property_type_key].loc[id_].to_dict()
    
    def add_properties(self, id_, property_type, properties=None):
        if id_ is None:
            raise ValueError('Must specify an ID')
        property_type_key = self._get_property_type_key(property_type)
        if property_type_key not in self.metadata:
            self.metadata[property_type_key] = pd.DataFrame(columns=self.columns(property_type))
        if id_ not in self.metadata[property_type_key].index:
            self.metadata[property_type_key].loc[id_, :] = None
            if properties:
                for p, v in properties.items():
                    self.metadata[property_type_key].loc[id_, p] = self._get_value_to_store(v)
        
    def delete_properties(self, id_, property_type):
        if id_ is None:
            raise ValueError('Must specify an ID')
        metadata = self.metadata.get(self._get_property_type_key(property_type), {})
        if id_ in metadata.index:
            metadata.drop(id_, inplace=True)
    
    def get_metadata(self, property_type):
        property_type_key = self._get_property_type_key(property_type)
        if property_type_key not in self.metadata:
            return None
        return self.metadata[property_type_key].T.to_dict()
    
    def set_metadata(self, property_type, value):
        property_type_key = self._get_property_type_key(property_type)
        self.metadata[property_type_key] = pd.DataFrame(value).T

    @staticmethod
    def columns(property_type):
        return [pt.name for pt in property_type]
    
    def _get_value_to_store(self, value):
        value_to_store = deepcopy(value)
        if isinstance(value_to_store, dict) or isinstance(value_to_store, list):
            value_to_store = 'json:' + json.dumps(value_to_store)
        return value_to_store
