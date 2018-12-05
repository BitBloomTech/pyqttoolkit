#pylint: disable=no-name-in-module
from PyQt5.Qt import QPushButton, QHBoxLayout, QSizePolicy, QPropertyAnimation, pyqtProperty, QEasingCurve, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty
from pyqttoolkit.colors import format_color, ColorFormat
from pyqttoolkit.services.theme_manager import ThemeManager
from .icon import Icon

class IconButton(QPushButton):
    def __init__(self, icon, title, parent, size=None, padding=None, color=None, hover_color=None):
        QPushButton.__init__(self, parent)
        self._theme_manager = ThemeManager.get(self)
        self._background_color = hover_color or self._theme_manager.get_color('button_background_hover')
        self.setToolTip(title)
        self._icon = Icon(self, icon, size, padding, color)
        self._iconname = icon

        self._layout = QHBoxLayout(self)
        self._layout.addWidget(self._icon)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._size = size
        self.setFlat(True)
        self._background_opacity = 0.0
        self._background_opacity_stop = 0.0
        self._update_style_sheet()
        self._animation = QPropertyAnimation(self, b'backgroundOpacity')
        self.clicked.connect(self._update_background_opacity_stop)
    
    @pyqtProperty(float)
    def backgroundOpacity(self):
        return self._background_opacity

    @backgroundOpacity.setter
    def backgroundOpacity(self, value):
        self._background_opacity = value
        self._update_style_sheet()
    
    def sizeHint(self):
        return self._size or self._icon.sizeHint()

    def enterEvent(self, event):
        if self.isEnabled():
            self._start_opacity_animation(350, 0, 1)
        return QPushButton.enterEvent(self, event)
    
    def leaveEvent(self, event):
        if self.isEnabled():
            self._start_opacity_animation(350, 1, 0)
        return QPushButton.leaveEvent(self, event)
    
    def mousePressEvent(self, event):
        if self.isEnabled():
            self._start_opacity_animation(50, 1, 0.6)
        return QPushButton.mousePressEvent(self, event)
    
    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            self._start_opacity_animation(50, self._background_opacity, 1)
        return QPushButton.mouseReleaseEvent(self, event)

    def _start_opacity_animation(self, duration, start, end):
        self._animation.stop()
        self._animation.setDuration(duration)
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.setEasingCurve(QEasingCurve.BezierSpline)
        self._animation.start()
    
    def setEnabled(self, value):
        QPushButton.setEnabled(self, value)
        self._icon.setEnabled(value)

    def _update_background_opacity_stop(self):
        self._background_opacity_stop = 0.0 if not self.isChecked() else 0.8
        self._update_style_sheet()

    def setChecked(self, value):
        QPushButton.setChecked(self, value)
        self._update_background_opacity_stop()

    def _update_style_sheet(self):
        stylesheet = """
Icon {{
    background-color: {color};
    border-radius: 2px;
}}
QPushButton {{
    background-color: transparent;
    border: none;
}}
""".format(color=format_color(self._background_color, ColorFormat.rgba_string_256, max(self._background_opacity, self._background_opacity_stop)))
        self.setStyleSheet(stylesheet)


class BindableIconButton(IconButton):
    def __init__(self, icon, title, parent, size=None, padding=None, color=None, hover_color=None):
        IconButton.__init__(self, icon, title, parent, size, padding, color, hover_color)
        self.setCheckable(True)
        self.clicked.connect(self._handle_clicked)
        self.checkedChanged.connect(self.setChecked)
    
    checkedChanged = pyqtSignal(bool)
    checked = AutoProperty(bool)

    def _handle_clicked(self):
        self.checked = self.isChecked()
