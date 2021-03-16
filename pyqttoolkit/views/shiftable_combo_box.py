from PyQt5.Qt import QHBoxLayout, QWidget, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QToolButton

from pyqttoolkit.properties import AutoProperty, bind
from .combo_box import BindableComboBox


class ShiftableComboBox(QWidget):
    """ComboBox with left and right shift buttons to decrease and increase the current index"""
    value = AutoProperty(str)
    valueChanged = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self._combo_box = BindableComboBox(self)
        self._left_shift = QToolButton(self)
        self._left_shift.setText('<')
        self._right_shift = QToolButton(self)
        self._right_shift.setText('>')

        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._left_shift)
        self._layout.addWidget(self._combo_box)
        self._layout.addWidget(self._right_shift)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        bind(self._combo_box, self, 'value')
        self._combo_box.currentIndexChanged.connect(self._handle_index_changed)
        self._left_shift.clicked.connect(self._handle_left_shift)
        self._right_shift.clicked.connect(self._handle_right_shift)

    @property
    def current_index(self):
        return self._combo_box.currentIndex()

    def setModel(self, model):
        self._combo_box.setModel(model)

    def _handle_left_shift(self):
        if self.current_index > 0:
            self._combo_box.setCurrentIndex(self.current_index - 1)

    def _handle_right_shift(self):
        if self.current_index < self._combo_box.count() - 1:
            self._combo_box.setCurrentIndex(self.current_index + 1)

    def _handle_index_changed(self):
        self._left_shift.setEnabled(self.current_index > 0)
        self._right_shift.setEnabled(self.current_index < self._combo_box.count() - 1)
