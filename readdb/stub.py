#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of ReadDB Visitor.
#               Developers can use this file as an example when implementing
#               additional information sources
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

def getInstance():
    return StubVisitor()

## this is a stub db reader. It provides an template that provides all
#  required functionality for an db reader
class StubVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, obj ):
        try:
            return obj['type'] == 'stub'
        except Exception as e:
            return False

    ##parse and return data specified in obj.
    # @return 'identifier' -> BalanceData map or exception.
    def visit(self, obj):
        return {}