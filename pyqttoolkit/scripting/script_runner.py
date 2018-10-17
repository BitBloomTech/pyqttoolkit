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
    def __init__(self, context):
        self._context = context
    
    def write(self, value):
        self._context.add_output(value)

@contextmanager
def redirect_output(context):
    writer = ContextWriter(context)
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
    def __init__(self, additional_paths=None):
        self._disallowed_modules = [
            r'sift', r'\binspect\b', r'\bimp\b', r'\bsys\b', r'\b\.', r'\bbuiltins\b'
        ]
        self._disallowed_globals = [
            '_', 'quit', 'eval', 'exec', 'help'
        ]
        self._additional_paths = additional_paths or []
        self._context = None

    def run(self, script, context):
        script = re.sub(r'(?<!\w)result(?!\w)', 'result[\'value\']', script)
        code = self.compile(script)
        try:
            self._context = context
            with redirect_output(self._context):
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
