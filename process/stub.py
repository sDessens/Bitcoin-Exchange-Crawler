# Module is stub implementation of Process Visitor.
# Developers can use this file as an example when implementing
# their own visitors.


## This function is required for every Visitor module
def getInstance():
    return StubVisitor()

## this is a stub Process visitor. It provides an template that provides
#  all required functionality for an Process visitor
class StubVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    ## run the process algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  @return the full, post-processed, list of resources
    #  may return exception
    def visit( self, json, resources ):
        resources.report( 'stub process visitor report' )

        # this stub visitor doesn't actually add resources.
        # if you're writing your own process visitor, take a look at how sum.py handles stuff
        return resources