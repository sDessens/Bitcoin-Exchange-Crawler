import common.balanceData
from common.writeable.collection import Resource

class PartialBalance(Resource):
    def __init__(self, value):
        assert isinstance( value, float )
        self.value = value

    def __str__(self):
        return 'PartialBalance({0})'.format(self.value)
