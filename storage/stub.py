
def getInstance():
    return StubVisitor()

##
# this is a stub storage visitor. It provides an template that provides all
#required functionality for an storage visitor
class StubVisitor:
    def __init__(self):
        pass

    ##
    # return True if this visitor accepts the given object.
    # False otherwise
    def accept( self, obj ):
        try:
            return obj['type'] == 'stub'
        except Exception as e:
            return False

    def visit( self, obj ):
        return StubStorage()


class StubStorage:
    def __init__(self):
        pass;
    
    ##The read function that downloads the data and returns a BalanceData object
    # @param identifier a string that identifies the file it will be written to.
    # @param fromTime the timeStamp from which the data should be returned
    # @param toTime the until what timeStamp data should be fetched
    def read(self,identifier,fromTime,toTime):
        return 0

    ##The write function that adds the value to the file in dropbox
    # @param identifier a string that identifies the file it will be written to.
    # @param value the value that should be writen
    def write(self,identifier,value):
        print 'StubStorage: write value', value, 'to', identifier
