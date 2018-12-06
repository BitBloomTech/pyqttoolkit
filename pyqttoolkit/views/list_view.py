#pylint: disable=no-name-in-module
from PyQt5.Qt import QListView, pyqtSignal
#pylint: enable=no-name-in-module

from pyqttoolkit.properties import AutoProperty

class ListView(QListView):
    def __init__(self, parent):
        QListView.__init__(self, parent)
        self.selectedIndexChanged.connect(self._handle_selected_index_changed)
        self._updating_selection = False
    
    selectedItemsChanged = pyqtSignal()
    selectedIndexChanged = pyqtSignal(int)

    selectedIndex = AutoProperty(int)
    
    def selectionChanged(self, current_selection, previous_selection):
        self._updating_selection = True
        result = QListView.selectionChanged(self, current_selection, previous_selection)
        self.selectedIndex = current_selection.indexes()[0].row() if current_selection.indexes() else -1
        self.selectedItemsChanged.emit()
        self._updating_selection = False
        return result

    def _handle_selected_index_changed(self, index):
        if self.model() is not None and not self._updating_selection:
            self.setCurrentIndex(self.model().createIndex(index, 0))
