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
""":mod:`task_runner`
Defines the task runner
"""
import logging
import inspect

#pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.Qt import QThreadPool, QRunnable, QThread, QSemaphore, QEvent, QCoreApplication
#pylint: enable=no-name-in-module

from concurrent.futures import ThreadPoolExecutor

from ..properties import AutoProperty

LOGGER = logging.getLogger(__name__)

class BusyArgs(QObject):
    def __init__(self, busy, indeterminate=True, cancellable=False, description=None):
        QObject.__init__(self, None)
        self._busy = busy
        self._indeterminate = indeterminate
        self._cancellable = cancellable
        self._description = description
        self._progress = 0
    
    cancelled = pyqtSignal()
    cancelComplete = pyqtSignal()
    progressChanged = pyqtSignal(float, str)

    @property
    def description(self):
        return self._description

    @property
    def progress(self):
        return self._progress

    def updateProgress(self, progress, description):
        self._progress = max(99, float(progress))
        self._description = description
        self.progressChanged.emit(progress, description)

    @property
    def busy(self):
        return self._busy

    @property
    def indeterminate(self):
        return self._indeterminate
    
    @property
    def cancellable(self):
        return self._cancellable
    
    def cancel(self):
        if self._cancellable:
            self.cancelled.emit()

class TaskCancelled(Exception):
    pass

class Worker:
    def __init__(self, task_runner, f, args, busy_args, on_completed, on_cancelled, on_error, error_description):
        self._task_runner = task_runner
        self._f = f
        self._args = args
        self._busy_args = busy_args
        self._on_completed = on_completed
        self._on_cancelled = on_cancelled
        self._on_error = on_error
        self._error_description = error_description
    
    def run(self):
        if self._busy_args:
            QCoreApplication.postEvent(self._task_runner, BusyEvent(self._busy_args))
        try:
            result = self._f(*self._args.args, **self._args.kwargs)
        except TaskCancelled:
            QCoreApplication.postEvent(self._task_runner, CancelledEvent(self._on_cancelled))
        #pylint: disable=broad-except
        except Exception as e:
            QCoreApplication.postEvent(self._task_runner, ErrorEvent(e, self._on_error, self._error_description))
        #pylint: enable=broad-except
        else:
            QCoreApplication.postEvent(self._task_runner, ResultEvent(result, self._on_completed))

class ProgressUpdatedEvent(QEvent):
    def __init__(self, progress, message):
        super().__init__(QEvent.User)
        self._progress = progress
        self._message = message
    
    @property
    def progress(self):
        return self._progress
    
    @property
    def message(self):
        return self._message

class CancelledEvent(QEvent):
    def __init__(self, on_cancelled):
        super().__init__(QEvent.User)
        self._on_cancelled = on_cancelled
    
    @property
    def on_cancelled(self):
        return self._on_cancelled

class ResultEvent(QEvent):
    def __init__(self, result, on_completed=None):
        super().__init__(QEvent.User)
        self._result = result
        self._on_completed = on_completed
    
    @property
    def result(self):
        return self._result
    
    @property
    def on_completed(self):
        return self._on_completed

class ErrorEvent(QEvent):
    def __init__(self, exception, on_error, error_description):
        super().__init__(QEvent.User)
        self._exception = exception
        self._on_error = on_error
        self._error_description = error_description
    
    @property
    def exception(self):
        return self._exception
    
    @property
    def on_error(self):
        return self._on_error
    
    @property
    def error_description(self):
        return self._error_description

class BusyEvent(QEvent):
    def __init__(self, busy_args):
        super().__init__(QEvent.User)
        self._busy_args = busy_args
    
    @property
    def args(self):
        return self._busy_args

class TaskArgs:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

class TaskRunner(QObject):
    """class::TaskRunner
    Runs tasks on a background thread
    """
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._is_cancelled = False
        self._executor = ThreadPoolExecutor(max_workers=1)

    def run_task(self, task_function, task_args=None, on_completed=None, on_cancelled=None, on_error=None, description=None, error_description=None, show_progress=True, cancellable=False, **kwargs):
        """function::runTask(self, task_function, task_args, on_completed, on_error)
        :param task_function: The function to execute
        :param task_args: The arguments to pass to the function
        :param on_completed: The function to execute when the task completes
        :param on_error: The function to execute when the task errors
        """
        LOGGER.info('Starting task "%s"...', description)
        task_args = task_args or []

        kwargs = {}

        parameters = inspect.signature(task_function).parameters

        if 'update_progress' in parameters:
            kwargs['update_progress'] = self.update_progress
            indeterminate = False
        else:
            indeterminate = True

        busy_args = BusyArgs(True, indeterminate, cancellable, description) if show_progress else None

        worker = Worker(
            self, task_function, TaskArgs(task_args, kwargs),
            busy_args=busy_args, on_completed=on_completed,
            on_cancelled=on_cancelled, on_error=on_error,
            error_description=error_description
        )
        self._executor.submit(worker.run)
    
    def update_progress(self, percent, message):
        QCoreApplication.postEvent(self, ProgressUpdatedEvent(float(percent), message))
    
    def event(self, event):
        if isinstance(event, ProgressUpdatedEvent):
            if self.busy is not None:
                self.busy.updateProgress(float(event.progress), event.message)
            return True
        elif isinstance(event, BusyEvent):
            self.busy = event.args
            self.busy.cancelled.connect(self.cancel)
            return True
        elif isinstance(event, ResultEvent):
            LOGGER.info('Task complete')
            self.reset()
            if event.on_completed is not None:
                event.on_completed(event.result)
            self.taskCompleted.emit()
            return True
        elif isinstance(event, CancelledEvent):
            LOGGER.info('Task cancelled')
            self.reset()
            self.busy.cancelComplete.emit()
            self.taskCancelled.emit()
            if event.on_cancelled is not None:
                event.on_cancelled()
            return True
        elif isinstance(event, ErrorEvent):
            LOGGER.info('Task error')
            self.reset()
            LOGGER.info('Error running task: %s', event.exception)
            if event.error_description is not None:
                self.error.emit(event.error_description)
                self.taskErrored.emit()
            elif event.on_error is not None:
                event.on_error(event.exception)
                self.taskErrored.emit()
            else:
                raise event.exception
            return True
        return super().event(event)
    
    def cancel(self):
        if not self._is_cancelled:
            if self.busy:
                self.busy.updateProgress(self.busy.progress, self.tr('Cancelling...'))
            self._is_cancelled = True
    
    def isCancelled(self):
        return self._is_cancelled
    
    def raiseForCancelled(self):
        if self._is_cancelled:
            raise TaskCancelled()

    def reset(self):
        self.busy = BusyArgs(False, description=None)
        self._is_cancelled = False
    
    busyChanged = pyqtSignal(BusyArgs)
    error = pyqtSignal(str)
    cancelComplete = pyqtSignal()
    taskCompleted = pyqtSignal()
    taskCancelled = pyqtSignal()
    taskErrored = pyqtSignal()

    busy = AutoProperty(BusyArgs)
