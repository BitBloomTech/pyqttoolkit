from enum import Enum

#pylint: disable=no-name-in-module
from PyQt5.Qt import QItemDelegate
#pylint: enable=no-name-in-module

from pyqttoolkit.models.roles import DataRole
from pyqttoolkit.views import BindableComboBox

class ComboBoxItemDelegate(QItemDelegate):
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)
    
    def setComboBoxModel(self, model):
        self._combo_box_model = model
    
    def createEditor(self, parent, option, index):
        combo_box = BindableComboBox(parent)
        combo_box.setModel(self._combo_box_model)
        value = self.parent().model().data(index, DataRole)
        if isinstance(value, Enum):
            value = value.name
        combo_box.value = value
        combo_box.currentIndexChanged.connect(self.closeEditor(combo_box))
        return combo_box
    
    def setEditorData(self, editor, index):
        editor.showPopup()

    def closeEditor(self, control):
        def _handler():
            self.parent().commitData(control)
            self.parent().closeEditor(control, QItemDelegate.NoHint)
        return _handler
