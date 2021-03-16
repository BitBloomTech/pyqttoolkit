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
from PyQt5.Qt import QWidget, QHBoxLayout, QLabel


def make_labelled(parent, label: str, widget: QWidget):
    """Put a widget into a container with a label to the left of it. Like a single row of a `QFormLayout`"""
    container = QWidget(parent)
    label_widget = QLabel(label)
    layout = QHBoxLayout(container)
    layout.setSpacing(0)
    layout.addWidget(label_widget)
    layout.addWidget(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    return container
