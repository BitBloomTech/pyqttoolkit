import re
import builtins

class ScriptRunner:    
    def __init__(self):
        self._disallowed_modules = [
            r'sift', r'\binspect\b', r'\bimp\b', r'\bsys\b', r'\bos\b', r'\b\.', r'\bbuiltins\b'
        ]

    def run(self, script, context):
        script = re.sub(r'(?<!\w)result(?!\w)', 'result[\'value\']', script)
        code = self.compile(script)
        #pylint: disable=exec-used
        exec(code, {'__builtins__': {'__import__': self._import, 'open': self._open, 'print': context.add_output, 'len': len}}, context.locals)
        #pylint: enable=exec-used

    def compile(self, script):
        return compile(script, 'code', 'exec')
    
    def _import(self, module, *args, **kwargs):
        if any(re.match(m, module) for m in self._disallowed_modules):
            raise ImportError('Module not found')
        try:
            return builtins.__import__(module, *args, **kwargs)
        except KeyError:
            raise ImportError('Module not found')

    def _open(self, file, *args, **kwargs):
        mode = args[0]
        if 'r' not in mode:
            raise ValueError('Writing of files not permitted')
        return open(file, *args, **kwargs)
