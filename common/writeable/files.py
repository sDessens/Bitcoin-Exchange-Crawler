class Files:
    def __init__(self):
        self._d = {}

    def items(self):
        return self._d.items()

    def addFile(self, key, path ):
        assert isinstance( path, str )
        assert key not in self._d
        self._d[key] = path

    def __str__(self):
        return str(self._d)