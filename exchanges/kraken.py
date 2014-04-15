
def getInstance():
    return KrakenVisitor()

class KrakenVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['name'] == 'kraken'
        except Exception as e:
            return False

    def visit( self, obj ):
        # todo return balance
        pass