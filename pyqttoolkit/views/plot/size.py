from mpl_toolkits.axes_grid1 import Size

class ToggleableFixed(Size._Base):
    def __init__(self, size):
        self._size = size
        self._active = False

    def activate(self):
        self._active = True
    
    def deactivate(self):
        self._active = False

    def get_size(self, _renderer):
        return 0.0, self._size if self._active else 0.0