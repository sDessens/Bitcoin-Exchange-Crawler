import common.balanceData

class SingleDatapoint:
    def __init__(self):
        self._d = {}

    def items(self):
        return self._d.items()

    def addBalance(self, key, value):
        assert isinstance( value, common.balanceData.BalanceData )
        assert key not in self._d
        self._d[key] = value

    def __str__(self):
        return str(self._d)
