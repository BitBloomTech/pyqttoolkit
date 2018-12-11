import logging
from logging import handlers
from functools import wraps
from os import path, makedirs
from enum import Enum

#pylint: disable=no-name-in-module
from PyQt5.Qt import QStandardPaths
#pylint: enable=no-name-in-module

class CustomLogLevel(Enum):
    TRACE = 5

TRACE = CustomLogLevel.TRACE.value

def get_log_dir():
    app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    return path.join(app_data, 'logs')

def get_log_file(log_dir):
    return path.join(log_dir, 'app.log')

def configure_logging(log_level, console):
    logging.addLevelName(TRACE, 'TRACE')

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        enum_level = getattr(CustomLogLevel, log_level.upper(), None)
        if isinstance(enum_level, CustomLogLevel):
            numeric_level = enum_level.value
        else:
            numeric_level = logging.INFO

    logging.getLogger().setLevel(numeric_level)

    rollover_bytes = 100 * 1024
    dir_name = get_log_dir()
    if not path.isdir(dir_name):
        makedirs(dir_name)

    file_handler = handlers.RotatingFileHandler(
        get_log_file(dir_name),
        mode='w',
        maxBytes=rollover_bytes,
        backupCount=10
    )
    file_handler.doRollover()
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logging.getLogger().addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(console_handler)

def log_debug(_f):
    return logf(logging.DEBUG)

def logf(level, log_args=True):
    def logf_decorator(f):
        @wraps(f)
        def _(*args, **kwargs):
            logger = logging.getLogger(f.__name__)
            if log_args:
                logger.log(level, 'Entering, args: %s, kwargs: %s', args, kwargs)
            else:
                logger.log(level, f'Entering')
            result = f(*args, **kwargs)
            logger.debug('Exiting')
            return result
        return _
    return logf_decorator
