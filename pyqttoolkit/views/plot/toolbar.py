#pylint: disable=no-name-in-module
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QWidget, Qt, QSize
from PyQt5.QtWidgets import QVBoxLayout
#pylint: enable=no-name-in-module

from pyqttoolkit.views import IconButton
from .tool_type import ToolType

class PlotToolbarWidget(QWidget):
    tool_icons = {
        ToolType.zoom: 'zoom.svg',
        ToolType.reset: 'crosshair.svg',
        ToolType.polygon: 'polygon.svg',
        ToolType.pan: 'pan.svg',
        ToolType.span: 'width.svg',
        ToolType.options: 'options.svg'
    }

    def __init__(self, parent, plotview):
        QWidget.__init__(self, parent)
        self._plotview = plotview
        self._tools = []
        self._extra_tools = []

        self._tool_names = {
            ToolType.reset: self.tr('Reset'),
            ToolType.zoom: self.tr('Zoom to Selection'),
            ToolType.polygon: self.tr('Draw Polygon'),
            ToolType.pan: self.tr('Pan'),
            ToolType.span: self.tr('Span'),
            ToolType.options: self.tr('Options'),
        }

        self._reset = IconButton(self.tool_icons[ToolType.reset], self._tool_names[ToolType.reset], self, QSize(30, 30), 4)
        self._reset.clicked.connect(self._plotview.resetZoom)

        for tool_type in [t for t in ToolType if plotview.toolAvailable(t)]:
            tool = self._create_tool(tool_type)
            self._tools.append((tool, tool_type))
            tool.setChecked(plotview.isActiveDefault(tool_type))

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._reset)
        for widget, tool_type in self._tools:
            self._layout.addWidget(widget)
            widget.setEnabled(self._plotview.toolEnabled(tool_type))
        self.setLayout(self._layout)
        self._plotview.enabledToolsChanged.connect(self._update_enabled)

    toolActivated = pyqtSignal(ToolType, bool)

    def _create_tool(self, tool_type):
        tool = IconButton(self.tool_icons[tool_type], self._tool_names[tool_type], self, QSize(30, 30), 4)
        tool.setCheckable(True)
        tool.clicked.connect(self._activate_tool(tool, tool_type))
        return tool

    def _activate_tool(self, button, tool_type):
        def _():
            for tool, other_type in self._tools:
                if tool != button:
                    tool.setChecked(False)
                    self._plotview.activateTool(other_type, False)
                    self.toolActivated.emit(other_type, False)
            self._plotview.activateTool(tool_type, button.isChecked())
            self.toolActivated.emit(tool_type, button.isChecked())
        return _

    def _update_enabled(self):
        for widget, tool_type in self._tools:
            widget.setEnabled(self._plotview.toolEnabled(tool_type))
