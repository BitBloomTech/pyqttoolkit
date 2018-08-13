class InvalidDataError(Exception):
    def __init__(self, name, error):
        Exception.__init__(self, f'{name}: {error}')
