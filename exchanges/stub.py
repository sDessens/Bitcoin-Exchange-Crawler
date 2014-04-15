
def getInstance():
    return StubVisitor()

"""
this is a stub exchange visitor. It provides an template that provides all
required functionality for an exchange visitor
"""
class StubVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['name'] == 'stub'
        except Exception as e:
            return False

    def visit( self, obj ):
        pass