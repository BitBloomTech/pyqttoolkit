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
from contextlib import contextmanager
import re
import builtins
import sys
import importlib

@contextmanager
def add_paths(paths):
    for path in paths:
        sys.path.insert(0, path)
    try:
        yield
    finally:
        for path in paths:
            sys.path.remove(path)

class ContextWriter:
    def __init__(self, context, skip_empty_output_lines=False):
        self._context = context
        self._skip_empty_output_lines = skip_empty_output_lines
    
    def write(self, value):
        if (value is not None and value.strip()) or not self._skip_empty_output_lines:
            self._context.add_output(value)

@contextmanager
def redirect_output(context, skip_empty_output_lines=False):
    writer = ContextWriter(context, skip_empty_output_lines)
    _stdout = sys.stdout
    sys.stdout = writer
    try:
        yield
    finally:
        sys.stdout = _stdout

class ScriptStopped(Exception):
    def __init__(self):
        Exception.__init__(self)

class ScriptRunner:    
    def __init__(self, additional_paths=None, skip_empty_output_lines=False):
        self._disallowed_modules = [
            r'sift', r'\binspect\b', r'\bimp\b', r'\bsys\b', r'\b\.', r'\bbuiltins\b'
        ]
        self._disallowed_globals = [
            '_', 'quit', 'eval', 'exec', 'help'
        ]
        self._additional_paths = additional_paths or []
        self._context = None
        self._skip_empty_output_lines = skip_empty_output_lines

    def run(self, script, context):
        script = re.sub(r'(?<!\w)result(?!\w)', 'result[\'value\']', script)
        code = self.compile(script)
        try:
            self._context = context
            with redirect_output(self._context, self._skip_empty_output_lines):
                #pylint: disable=exec-used
                exec(code, self._globals(context), context.locals)
                #pylint: enable=exec-used
        except ScriptStopped:
            pass
        finally:
            self._context = None
        
    def _globals(self, context):
        return {'__builtins__': {**__builtins__, '__import__': self._import, 'exit': self._exit, **{g: self._not_implemented for g in self._disallowed_globals}}}

    def compile(self, script):
        return compile(script, 'code', 'exec')
    
    def _import(self, module_name, *args, **kwargs):
        if any(re.match(m, module_name) for m in self._disallowed_modules):
            raise ImportError('Module not found')
        try:
                
            with add_paths(self._additional_paths):
                module = builtins.__import__(module_name, *args, **kwargs)
            return module
        except KeyError:
            raise ImportError('Module not found')
    
    def _additional_paths(self):
        return self._additional_paths
    
    def _exit(self):
        raise ScriptStopped()
    
    def add_path(self, path):
        if path in self._additional_paths:
            self._additional_paths.remove(path)
        self._additional_paths.insert(0, path)

    def _not_implemented(self, *args, **kwargs):
        raise NotImplementedError()
