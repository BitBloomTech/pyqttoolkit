import pytest
import time

from asyncio import Event, wait_for

#pylint: disable=no-name-in-module
from PyQt5.Qt import QApplication, QThread
#pyline: enable=no-name-in-module

from pyqttoolkit.services.task_runner import *

class Result:
    def __init__(self):
        self._value = None
    
    def set(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

@pytest.fixture
def task_runner(qtbot):
    app = QApplication([])
    yield TaskRunner(app)

def _handler(event, result=None):
    def _(value):
        event.set()
        if result:
            result.set(value)
    return _

@pytest.mark.asyncio
async def test_simple_task_completes(qtbot, task_runner):
    event = Event()
    with qtbot.waitSignal(task_runner.taskCompleted, timeout=1000):
        task_runner.run_task(lambda: 42, on_completed=_handler(event))
    await wait_for(event.wait(), 1)

@pytest.mark.asyncio
async def test_result_is_correct(qtbot, task_runner):
    event = Event()
    result = Result()
    with qtbot.waitSignal(task_runner.taskCompleted, timeout=1000):
        task_runner.run_task(lambda: 42, on_completed=_handler(event, result))
    await wait_for(event.wait(), 1)
    assert result.value == 42

@pytest.mark.asyncio
async def test_will_wait_for_cancel_lock_before_terminating(qtbot, task_runner):
    event_1 = Event()
    event_2 = Event()
    event_3 = Event()
    result = Result()
    def _task(cancel_lock):
        cancel_lock.acquire()
        result.set(42)
        event_1.set()
        while not event_2.is_set():
            pass
        result.set(24)
        cancel_lock.release()
        while not event_3.is_set():
            pass
    with qtbot.waitSignal(task_runner.taskCancelled, timeout=10000):
        task_runner.run_task(_task)
        await wait_for(event_1.wait(), 2)
        task_runner.cancel()
        event_2.set()
    assert result.value == 24

@pytest.mark.asyncio
async def test_will_wait_for_cancel_before_end(qtbot, task_runner):
    event_1 = Event()
    event_2 = Event()
    event_3 = Event()
    event_4 = Event()
    result = Result()
    def _task(cancel_lock):
        cancel_lock.acquire()
        result.set(42)
        event_1.set()
        while not event_2.is_set():
            pass
        result.set(24)
        event_3.set()
        cancel_lock.release()
        while not event_4.is_set():
            pass
        result.set(7)
    with qtbot.waitSignal(task_runner.taskCancelled, timeout=10000):
        task_runner.run_task(_task)
        await wait_for(event_1.wait(), 2)
        task_runner.cancel()
        event_2.set()
        await wait_for(event_3.wait(), 2)
    event_4.set()
    assert result.value == 24

@pytest.mark.asyncio
async def test_error_handler_called_if_error_raised(qtbot, task_runner):
    result = Result()
    event = Event()
    def _task():
        raise ValueError('value')
    with qtbot.waitSignal(task_runner.taskErrored, timeout=10000):
        task_runner.run_task(_task, on_error=_handler(event, result))
    await wait_for(event.wait(), 1)
    assert isinstance(result.value, ValueError)

@pytest.mark.qt_no_exception_capture
def test_error_raised_if_no_error_handler(qtbot, task_runner):
    event = Event()
    def _task():
        raise ValueError('value')
    with pytest.raises(ValueError):    
        with qtbot.waitSignal(task_runner.taskErrored, timeout=10000):
            task_runner.run_task(_task)

@pytest.mark.asyncio
async def test_can_queue_tasks(qtbot, task_runner):
    event_0 = Event()
    event_1 = Event()
    result_1 = Result()
    event_2 = Event()
    result_2 = Result()
    def _task(start_event):
        def _():
            while not start_event.is_set():
                pass
            return 42
        return _
    
    handler_1 = _handler(event_1, result_1)
    handler_2 = _handler(event_2, result_2)

    with qtbot.waitSignal(task_runner.taskCompleted, timeout=10000):
        task_runner.run_task(_task(event_0), on_completed=handler_1)
        task_runner.run_task(_task(event_1), on_completed=handler_2)
        event_0.set()
    
    with qtbot.waitSignal(task_runner.taskCompleted, timeout=10000):
        pass
    
    await wait_for(event_2.wait(), 2)
    assert result_1.value == 42
    assert result_2.value == 42
