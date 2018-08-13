class ScriptContext:
    def __init__(self, **kwargs):
        self._locals = kwargs
        self._result = {'value': None}
        self._output = ''
    
    @property
    def locals(self):
        return {**self._locals, 'result': self._result}
    
    @property
    def result(self):
        return self._result['value']
    
    @property
    def output(self):
        return self._output

    def add_output(self, *values):
        self._output += ' '.join(str(v) for v in values) + '\r\n'
