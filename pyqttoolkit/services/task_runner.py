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
from PyQt5.Qt import QThreadPool, QRunnable, QThread, QSemaphore
#pylint: enable=no-name-in-module

from ..properties import AutoProperty

LOGGER = logging.getLogger(__name__)

class BusyArgs(QObject):
    def __init__(self, busy, long_running=False, indeterminate=True, cancellable=False, description=None):
        QObject.__init__(self, None)
        self._busy = busy
        self._long_running = long_running
        self._indeterminate = indeterminate
        self._cancellable = cancellable
        self.description = description
    
    cancelled = pyqtSignal()
    cancelComplete = pyqtSignal()
    descriptionChanged = pyqtSignal(str)
    progressChanged = pyqtSignal(float)

    description = AutoProperty(str)
    progress = AutoProperty(float)
    
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

class Worker(QThread):
    def __init__(self, f, *args):
        QThread.__init__(self)
        self._f = f
        self._args = args
    
    result = pyqtSignal(object)
    error = pyqtSignal(object)

    def run(self):
        try:
            result = self._f(*self._args)
        #pylint: disable=broad-except
        except Exception as e:
            self.error.emit(e)
        #pylint: enable=broad-except
        else:
            self.result.emit(result)

class CancelWorker(QThread):
    def __init__(self, worker, cancel_lock):
        QThread.__init__(self)
        self._worker = worker
        self._cancel_lock = cancel_lock

    complete = pyqtSignal()
    
    def run(self):
        self._cancel_lock.acquire()
        self._worker.terminate()
        self.complete.emit()

class QueuedTask(QThread):
    def __init__(self, task_runner, **kwargs):
        QThread.__init__(self)
        self._task_runner = task_runner
        self._kwargs = kwargs
    
    complete = pyqtSignal()
    
    def run(self):
        self._task_runner._queue_semaphore.acquire()
        self._task_runner._run_task_no_queue(**self._kwargs)
        self.complete.emit()

class TaskRunner(QObject):
    """class::TaskRunner
    Runs tasks on a background thread
    """
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._current_worker = None
        self._cancel_lock = None
        self._cancel_worker = None
        self._current_on_error = None
        self._current_error_description = None
        self._current_show_progress = None
        self._current_on_completed = None
        self._queue_semaphore = QSemaphore(1)
        self._queued_tasks = []

    def run_task(self, task_function, task_args=None, on_completed=None, on_cancelled=None, on_error=None, description=None, error_description=None, long_running=False, show_progress=True, background=False):
        """function::runTask(self, task_function, task_args, on_completed, on_error)
        :param task_function: The function to execute
        :param task_args: The arguments to pass to the function
        :param on_completed: The function to execute when the task completes
        :param on_error: The function to execute when the task errors
        """
        if self._queue_semaphore.tryAcquire():
            self._run_task_no_queue(task_function, task_args, on_completed, on_cancelled, on_error, description, error_description, long_running, show_progress, background)
        else:
            task = QueuedTask(self, 
                task_function=task_function, 
                task_args=task_args, 
                on_completed=on_completed, 
                on_cancelled=on_cancelled, 
                on_error=on_error, 
                description=description, 
                error_description=error_description, 
                long_running=long_running, 
                show_progress=show_progress, 
                background=background
            )
            self._queued_tasks.append(task)
            task.complete.connect(lambda: self._queued_tasks.remove(task))
            task.start()
    
    def _run_task_no_queue(self, task_function, task_args=None, on_completed=None, on_cancelled=None, on_error=None, description=None, error_description=None, long_running=False, show_progress=True, background=False):
        LOGGER.info('Starting task "%s"...', description)
        task_args = task_args or []
        self._current_on_error = on_error
        self._current_error_description = error_description
        self._current_show_progress = show_progress
        self._current_on_completed = on_completed

        kwargs = {}

        parameters = inspect.signature(task_function).parameters

        if 'update_progress' in parameters:
            kwargs['update_progress'] = self.update_progress
            indeterminate = False
        else:
            indeterminate = True
        
        if 'cancel_lock' in parameters:
            self._cancel_lock = QSemaphore(1)
            kwargs['cancel_lock'] = self._cancel_lock
            cancellable = True
        else:
            cancellable = False
        
        task_delegate = lambda a: task_function(*a, **kwargs)

        if show_progress:
            self.busy = BusyArgs(True, long_running, indeterminate, cancellable, description)
            self.busy.cancelled.connect(self.cancel)

        self._current_worker = Worker(task_delegate, task_args)
        self._current_worker.result.connect(self._on_result)
        self._current_worker.error.connect(self._on_error)
        self._current_worker.start(QThread.NormalPriority if not background else QThread.LowPriority)
    
    def wait(self):
        if self._current_worker is None:
            return
        self._current_worker.wait()

    def update_progress(self, percent, message):
        self.busy.progress = float(percent)
        self.busy.description = message
    
    def cancel(self):
        if self._cancel_lock is not None:
            self.busy.description = self.tr('Cancelling...')
            self._cancel_worker = CancelWorker(self._current_worker, self._cancel_lock)
            self._cancel_worker.complete.connect(self._cancel_complete)
            self._cancel_worker.start()
        else:
            raise RuntimeError('Cannot cancel task, no cancel lock found')

    def _cancel_complete(self):
        self.resetWorker()
        try:
            self.busy.cancelComplete.emit()
            self.taskCancelled.emit()
        finally:
            self.resetTask()

    def _on_error(self, exception):
        self.resetWorker()
        try:
            LOGGER.info('Error running task: %s', exception)
            if self._current_error_description is not None and self._current_on_error is not None:
                self.error.emit(self._current_error_description)
                self.taskErrored.emit()
            elif self._current_on_error is not None:
                self._current_on_error(exception)
                self.taskErrored.emit()
            else:
                raise exception
        finally:
            self.resetTask()

    def _on_result(self, result):
        self.resetWorker()
        try:
            if self._current_on_completed is not None:
                self._current_on_completed(result)
            self.taskCompleted.emit()
        finally:
            self.resetTask()
    
    def resetWorker(self):
        self.busy = BusyArgs(False, description=None)
        LOGGER.info('Resetting task...')
        self._current_worker = None
        self._cancel_lock = None
        self._cancel_worker = None
    
    def resetTask(self):
        self._queue_semaphore.release()
        self._current_on_error = None
        self._current_error_description = None
        self._current_show_progress = None
        self._current_on_completed = None

    busyChanged = pyqtSignal(BusyArgs)
    error = pyqtSignal(str)
    cancelComplete = pyqtSignal()
    taskCompleted = pyqtSignal()
    taskCancelled = pyqtSignal()
    taskErrored = pyqtSignal()

    busy = AutoProperty(BusyArgs)
