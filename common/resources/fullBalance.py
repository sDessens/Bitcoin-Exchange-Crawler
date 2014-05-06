#this module implements an resource that stores an complete balance.


from common.resources.collection import Resource
from common.balanceData import BalanceData

class FullBalance(Resource):
    def __init__(self, balanceData ):
        assert isinstance( balanceData, BalanceData )
        self.value = balanceData

    def __str__(self):
        return 'FullBalance({0})'.format(hex(id(self.value)))