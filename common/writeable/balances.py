class Balances:
    def __init__(self):
        self._d = {}

    def items(self):
        return self._d.items()

    def addBalance(self, identifier, key):
        assert key not in self._d
        self._d[key] = identifier
