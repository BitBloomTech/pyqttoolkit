import pytest

from threading import Event

from pyqttoolkit.services.task_runner import TaskRunner
from pytestqt.exceptions import capture_exceptions


class Result:
    def __init__(self):
        self._value = None

    def set(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


@pytest.fixture
def task_runner(qapp):
    runner = TaskRunner(qapp)
    yield runner
    runner.shutdown()


def _wait_for(event):
    # Worker threads must always finish, including when a test assertion fails.
    assert event.wait(5), 'Timed out waiting for the test to release the worker'


def test_simple_task_completes(qtbot, task_runner):
    completed = Event()
    with qtbot.waitSignal(task_runner.taskCompleted, timeout=1000):
        task_runner.run_task(lambda: 42, on_completed=lambda value: completed.set())
    assert completed.is_set()


def test_result_is_correct(qtbot, task_runner):
    result = Result()
    with qtbot.waitSignal(task_runner.taskCompleted, timeout=1000):
        task_runner.run_task(lambda: 42, on_completed=result.set)
    assert result.value == 42


def test_will_terminate_on_cancel_check(qtbot, task_runner):
    started = Event()
    proceed = Event()
    result = Result()

    def task():
        result.set(42)
        started.set()
        _wait_for(proceed)
        result.set(24)
        task_runner.raiseForCancelled()
        result.set(7)

    try:
        with qtbot.waitSignal(task_runner.taskCancelled, timeout=2000):
            task_runner.run_task(task)
            qtbot.waitUntil(started.is_set, timeout=2000)
            task_runner.cancel()
            proceed.set()
        assert result.value == 24
    finally:
        proceed.set()


def test_will_wait_for_cancel_before_end(qtbot, task_runner):
    started = Event()
    proceed = Event()
    reached_cancel_check = Event()
    finish = Event()
    result = Result()

    def task():
        result.set(42)
        started.set()
        _wait_for(proceed)
        result.set(24)
        reached_cancel_check.set()
        task_runner.raiseForCancelled()
        _wait_for(finish)
        result.set(7)

    try:
        with qtbot.waitSignal(task_runner.taskCancelled, timeout=2000):
            task_runner.run_task(task)
            qtbot.waitUntil(started.is_set, timeout=2000)
            task_runner.cancel()
            proceed.set()
            qtbot.waitUntil(reached_cancel_check.is_set, timeout=2000)
        assert result.value == 24
    finally:
        proceed.set()
        finish.set()


def test_error_handler_called_if_error_raised(qtbot, task_runner):
    result = Result()

    def task():
        raise ValueError('value')

    with qtbot.waitSignal(task_runner.taskErrored, timeout=1000):
        task_runner.run_task(task, on_error=result.set)
    assert isinstance(result.value, ValueError)


def test_error_raised_if_no_error_handler(qtbot, task_runner):
    exception = ValueError('value')

    def task():
        raise exception

    with capture_exceptions() as exceptions:
        task_runner.run_task(task)
        qtbot.waitUntil(lambda: bool(exceptions), timeout=1000)
    assert len(exceptions) == 1
    assert exceptions[0][1] == exception


def test_can_queue_tasks(qtbot, task_runner):
    release_first = Event()
    first_completed = Event()
    completed = []
    signals = []
    task_runner.taskCompleted.connect(lambda: signals.append(True))

    def task(gate):
        def run():
            _wait_for(gate)
            return 42
        return run

    def complete_first(value):
        completed.append(('first', value))
        first_completed.set()

    try:
        task_runner.run_task(task(release_first), on_completed=complete_first)
        task_runner.run_task(
            task(first_completed),
            on_completed=lambda value: completed.append(('second', value)),
        )
        release_first.set()
        qtbot.waitUntil(lambda: len(signals) == 2, timeout=2000)
        assert completed == [('first', 42), ('second', 42)]
    finally:
        release_first.set()
        first_completed.set()
