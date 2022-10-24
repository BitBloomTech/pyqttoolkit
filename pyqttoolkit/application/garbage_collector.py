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
import gc
import logging

from PyQt5.QtCore import QObject, QTimer

from pyqttoolkit.logs import TRACE

LOGGER = logging.getLogger(__name__)

class GarbageCollector(QObject):
    '''
    Disable automatic garbage collection and instead collect manually
    every INTERVAL milliseconds.

    This is done to ensure that garbage collection only happens in the GUI
    thread, as otherwise Qt can crash.
    '''

    def __init__(self, parent, interval=60000):
        super().__init__(parent)
        self._interval = interval
        self._threshold = gc.get_threshold()
        gc.disable()

        if self._interval:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self.check)
            self._timer.start(self._interval)
        else:
            self._timer = None

    def check(self, full=False):
        l0, l1, l2 = gc.get_count()
        LOGGER.log(TRACE, 'gc_check called: l0=%d, l1=%d, l2=%d', l0, l1, l2)
        if full or l0 > self._threshold[0]:
            num = gc.collect(0)
            LOGGER.log(TRACE, 'Collecting gen 0, found: %d unreachable', num)
            if full or l1 > self._threshold[1]:
                num = gc.collect(1)
                LOGGER.log(TRACE, 'Collecting gen 1, found: %d unreachable', num)
                if full or l2 > self._threshold[2]:
                    num = gc.collect(2)
                    LOGGER.log(TRACE, 'Collecting gen 2, found: %d unreachable', num)

    def debug_cycles(self):
        gc.set_debug(gc.DEBUG_SAVEALL)
        gc.collect()
        for obj in gc.garbage:
            LOGGER.log(TRACE, "gc: obj=%s, (%s), type=%s", obj, repr(obj), type(obj))
