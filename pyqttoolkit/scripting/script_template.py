from datetime import datetime

from jinja2 import Environment

class ScriptTemplate:
    def __init__(self, template_string, name):
        self._template_string = template_string
        self._template_name = name
    
    def render(self, *args, **kwargs):
        environment = Environment()
        environment.globals.update(**self._get_globals())
        template = environment.from_string(self._template_string)
        return template.render(*args, **kwargs)
    
    def _get_globals(self):
        return {
            'zip': zip,
            'len': len,
            'template_name': self._template_name,
            'now': datetime.now().strftime('%Y-%m-%d %I:%M'),
            'indent': self._indent
        }
    
    def _indent(self, level):
        return '    ' * level
