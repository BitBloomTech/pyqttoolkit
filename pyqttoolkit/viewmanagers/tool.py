class ToolViewManager:
    def __init__(self, view, model):
        self._view = view
        self._model = model
    
    def save(self):
        raise NotImplementedError()
