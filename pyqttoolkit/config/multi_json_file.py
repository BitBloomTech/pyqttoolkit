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
from os import path, makedirs
from json import load, dump, JSONDecodeError
import logging
import shutil

from .base import BaseApplicationConfiguration

LOGGER = logging.getLogger(__name__)

class MultiJsonFileApplicationConfiguration(BaseApplicationConfiguration):
    def __init__(self, directory):
        self._directory = directory

    def get_value(self, key):
        parts = key.split('.')
        if len(parts) < 2:
            raise ValueError('key')

        filename = path.join(self._directory, f'{parts[0]}.json')
        value_path = parts[1:]

        if not path.exists(filename):
            return None

        try:
            with open(filename) as fp:
                values = load(fp)
        except JSONDecodeError as err:
            LOGGER.warning('Invalid json file, exception: %s', err)
            self._backup_file(filename)
            return None
        
        result = values
        for p in value_path:
            result = result.get(p, {})
        
        if result == {}:
            return None

        return result

    def _backup_file(self, filename):
        backup_path_root = path.join(path.dirname(filename), f'{path.basename(filename)}.json.bak')
        attempt = 0
        backup_path = backup_path_root
        while path.isfile(backup_path):
            attempt += 1
            backup_path = backup_path_root + f'.{attempt}'
        LOGGER.warning('Backing up config file %s to %s', filename, backup_path)
        shutil.move(filename, backup_path)

    def set_value(self, key, value):
        parts = key.split('.')
        if len(parts) < 2:
            raise ValueError('key')
        
        filename = path.join(self._directory, f'{parts[0]}.json')
        if path.exists(filename):
            try:
                with open(filename) as fp:
                    current_config = load(fp)
            except JSONDecodeError as err:
                LOGGER.warning('Invalid json file, exception: %s', err)
                current_config = {}
        else:
            current_config = {}
        
        parent = current_config
        for p in parts[1:-1]:
            parent = current_config.setdefault(p, {})
        parent[parts[-1]] = value

        if not path.isdir(path.dirname(filename)):
            makedirs(path.dirname(filename))

        with open(filename, 'w') as fp:
            dump(current_config, fp, indent=4, sort_keys=True)
