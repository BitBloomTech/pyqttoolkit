from os import path, makedirs
from json import load, dump, JSONDecodeError
import logging

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
            return None
        
        result = values
        for p in value_path:
            result = result.get(p, {})

        return result

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
