""":mod:`task_runner`
Defines the task runner
"""
import logging
import inspect

#pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.Qt import QThreadPool, QRunnable
#pylint: enable=no-name-in-module

from ..properties import AutoProperty

class BusyArgs(QObject):
    def __init__(self, busy, long_running=False, indeterminate=True, cancellable=False):
        QObject.__init__(self, None)
        self._busy = busy
        self._long_running = long_running
        self._indeterminate = indeterminate
        self._cancellable = cancellable
    
    cancelled = pyqtSignal()
    
    @property
    def busy(self):
        return self._busy

    @property
    def long_running(self):
        return self._long_running

    @property
    def indeterminate(self):
        return self._indeterminate
    
    @property
    def cancellable(self):
        return self._cancellable
    
    def cancel(self):
        if self._cancellable:
            self.cancelled.emit()

LOGGER = logging.getLogger(__name__)

class WorkerSignals(QObject):
    def __init__(self):
        QObject.__init__(self)
    
    error = pyqtSignal(object)
    result = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, f, *args):
        QRunnable.__init__(self)
        self._f = f
        self._args = args
        self._signals = WorkerSignals()
    
    @property
    def signals(self):
        return self._signals
    
    @pyqtSlot()
    def run(self):
        try:
            result = self._f(*self._args)
        #pylint: disable=broad-except
        except Exception as e:
            self.signals.error.emit(e)
        #pylint: enable=broad-except
        else:
            self.signals.result.emit(result)

class TaskRunner(QObject):
    """class::TaskRunner
    Runs tasks on a background thread
    """
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._threadpool = QThreadPool()
        self._cancelled = False

    def run_task(self, task_function, task_args, on_completed=None, on_cancelled=None, on_error=None, description=None, error_description=None, long_running=False, show_progress=True):
        """function::runTask(self, task_function, task_args, on_completed, on_error)
        :param task_function: The function to execute
        :param task_args: The arguments to pass to the function
        :param on_completed: The function to execute when the task completes
        :param on_error: The function to execute when the task errors
        """

        def _on_error(exception):
            if show_progress:
                self.busy = BusyArgs(False)
                self.description = None
            LOGGER.info('Error running task: %s', exception)
            if error_description is not None and on_error is not None:
                self.error.emit(error_description)
            elif on_error is not None:
                on_error(exception)
            else:
                raise exception

        def _on_result(result):
            if show_progress:
                self.busy = BusyArgs(False)
                self.description = None
            if not self._cancelled and on_completed is not None:
                on_completed(result)
            if self._cancelled and on_cancelled is not None:
                on_cancelled(result)

        kwargs = {}

        if 'update_progress' in inspect.signature(task_function).parameters:
            kwargs['update_progress'] = self.update_progress
            indeterminate = False
        else:
            indeterminate = True
        
        if 'is_cancelled' in inspect.signature(task_function).parameters:
            kwargs['is_cancelled'] = self.is_cancelled
            cancellable = True
        else:
            cancellable = False

        task_delegate = lambda a: task_function(*a, **kwargs)

        self._cancelled = False
        if show_progress:
            self.busy = BusyArgs(True, long_running, indeterminate, cancellable)
            self.busy.cancelled.connect(self.cancel)
            self.description = description

        worker = Worker(task_delegate, task_args)
        worker.signals.result.connect(_on_result)
        worker.signals.error.connect(_on_error)
        self._threadpool.start(worker)

    def update_progress(self, percent, message):
        self.progress = float(percent)
        self.description = message
    
    def is_cancelled(self):
        return self._cancelled
    
    def cancel(self):
        self._cancelled = True

    busyChanged = pyqtSignal(BusyArgs)
    descriptionChanged = pyqtSignal(str)
    progressChanged = pyqtSignal(float)
    error = pyqtSignal(str)

    busy = AutoProperty(BusyArgs)
    description = AutoProperty(str)
    progress = AutoProperty(float)
