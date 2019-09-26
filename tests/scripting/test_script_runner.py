import pytest

from pyqttoolkit.scripting import ScriptContext, ScriptRunner

def test_script_runner_can_run_script_no_locals():
    ScriptRunner().run('result = "hello"', ScriptContext())

def test_error_raised_when_variable_not_defined():
    with pytest.raises(NameError):
        ScriptRunner().run('b = a + 1', ScriptContext())

def test_script_runner_can_modify_locals():
    context = ScriptContext()
    ScriptRunner().run('result = 42', context)
    assert context.result == 42

def test_can_use_result_in_script_elsewhere():
    script = """result_temp = 42
result = result_temp * 2
"""
    context = ScriptContext()
    ScriptRunner().run(script, context)
    assert context.result == 84

@pytest.mark.parametrize('module', [
    'inspect', 'sift.__main__', 'sift'
])
def test_cannot_import_blacklisted_module(module):
    script = f"""import {module}
"""
    with pytest.raises(ImportError):
        ScriptRunner().run(script, ScriptContext())

@pytest.mark.parametrize('module', [
    'math', 'pandas'
])
def test_can_import_non_blacklisted_module(module):
    script = f"""import {module}

"""
    ScriptRunner().run(script, ScriptContext())

def test_cannot_import_relative_module():
    script = 'from . import builtins'
    with pytest.raises(ImportError):
        ScriptRunner().run(script, ScriptContext())

def test_can_import_from_pandas():
    script = 'from pandas import isna'
    ScriptRunner().run(script, ScriptContext())

def test_can_run_recursive_function():
    script = """def fact(a):
    if a <= 1:
        return 1
    print(globals())
    return a * fact(a - 1)

fact(3)
"""
    ScriptRunner().run(script, ScriptContext())
