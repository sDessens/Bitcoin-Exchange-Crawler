class FullBalance:
    def __init__(self):
        self._d = {}

    def addBalance(self, key, value):
        assert key not in self._d
        self._d[key] = value

    def items(self):
        return self._d.items()

    def __str__(self):
        assert False, "not implemented"