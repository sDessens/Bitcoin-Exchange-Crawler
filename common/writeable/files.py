class Files:
    def __init__(self):
        self._d = {}

    def items(self):
        return self._d.items()

    def addFile(self, path, key ):
        assert key not in self._d
        self._d[key] = path