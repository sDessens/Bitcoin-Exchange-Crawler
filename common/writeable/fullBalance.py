from common.writeable.collection import Resource

class FullBalance(Resource):
    def __init__(self, balanceData ):
        self.value = balanceData

    def __str__(self):
        return 'FullBalance({0})'.format(hex(id(self.value)))