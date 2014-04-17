import balanceData

def getInstance():
    return StubVisitor()

##
# this is a stub storage visitor. It provides an template that provides all
# required functionality for an storage visitor
class StubVisitor:
    def __init__(self):
        pass

    ##
    # @return True if this visitor accepts the given object.
    def accept( self, obj ):
        try:
            return obj['type'] == 'stub'
        except Exception as e:
            return False

    ##
    # @return some object with read and write functions
    def visit(self, obj):
        return StubStorage()


class StubStorage:
    def __init__(self):
        pass;
    
    ##The read function returns an BalanceData object uniquely identified with parameter identifier
    # @param identifier a string that uniquely identifies the source
    # @param fromTime An Unix timestamp that marks the begin of the data
    # @param toTime An Unix timestamp that marks the end of the data
    def read(self, identifier, fromTime = 0, toTime = 2000000000): # 1970 to 2033
        return balanceData.BalanceData([100,200,300], [1,1.5,1.2])

    ##The write function appends given value to to the data
    # @param identifier an string that uniquely identifies the target
    # @param value the value that should be writen
    def write(self, identifier, value):
        print 'StubStorage: write value', value, 'to', identifier
