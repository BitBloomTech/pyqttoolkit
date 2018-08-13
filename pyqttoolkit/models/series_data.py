""":mod:`series_data`
Defines the SeriesDataModel
"""

#pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject
#pylint: enable=no-name-in-module

class SeriesDataModel(QObject):
    """class::SeriesDataModel
    Wraps a series to be displayed
    """
    #pylint: disable=too-many-arguments
    def __init__(
            self, parent,
            x_axis_title, y_axis_title,
            x_axis_extent, y_axis_extent,
            zoom_flag, empty
    ):
        QObject.__init__(self, parent)

        self._x_axis_title = x_axis_title
        self._y_axis_title = y_axis_title
        self._x_axis_extent = x_axis_extent
        self._y_axis_extent = y_axis_extent
        self._zoom_flag = zoom_flag
        self._empty = empty

    def get_xy_extents(self):
        return self._x_axis_extent, self._y_axis_extent

    @property
    def is_empty(self):
        return self._empty

    @property
    def zoom_flag(self):
        return self._zoom_flag

    @property
    def xAxisTitle(self):
        """function::xAxisTitle(self)
        Property accessor for xAxisTitle
        """
        return self._x_axis_title

    @property
    def yAxisTitle(self):
        """function::yAxisTitle(self)
        Property accessor for yAxisTitle
        """
        return self._y_axis_title
