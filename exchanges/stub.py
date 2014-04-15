
def getInstance():
    return StubVisitor()

"""
this is a stub exchange visitor. It provides an template that provides all
required functionality for an exchange visitor
"""
class StubVisitor:
    def __init__(self):
        pass

    """
    return True if this visitor accepts the given object.
    False otherwise
    """
    def accept( self, obj ):
        try:
            return obj['name'] == 'stub'
        except Exception as e:
            return False

    """
    return this balance of this exchange, or throw an exception if an error
    occurs.
    """
    def visit( self, obj ):
        return 0