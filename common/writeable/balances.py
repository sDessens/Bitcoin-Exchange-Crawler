class Balances:
    def __init__(self):
        self._d = {}

    def items(self):
        return self._d.items()

    def addBalance(self, key, value):
        assert key not in self._d
        self._d[key] = value
