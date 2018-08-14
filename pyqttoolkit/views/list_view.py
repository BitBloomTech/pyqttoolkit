#pylint: disable=no-name-in-module
from PyQt5.Qt import QListView, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class ListView(QListView):
    def __init__(self, parent):
        QListView.__init__(self, parent)
    
    selectedItemsChanged = pyqtSignal()
    selectedIndexChanged = pyqtSignal(int)

    selectedIndex = AutoProperty(int)
    
    def selectionChanged(self, current_selection, previous_selection):
        result = QListView.selectionChanged(self, current_selection, previous_selection)
        self.selectedIndex = current_selection.indexes()[0].row() if current_selection.indexes() else -1
        self.selectedItemsChanged.emit()
        return result