#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of Exchange Visitor. Developers
#               can use this file as an example when implementing balance
#               crawlers for additional exchanges
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

from common.writeable.balances import Balances


## This functon is required for every Exchange Visitor module
#
def getInstance():
    return StubVisitor()


## this is a stub exchange visitor. It provides an template that provides all
#  required functionality for an exchange visitor
class StubVisitor:
    def __init__(self):
        pass

    ## return True if this visitor accepts the given object.
    #  False otherwise
    def accept( self, obj ):
        try:
            return obj['type'] == 'stub'
        except Exception as e:
            return False

    ## return this balance of this exchange, or throw an exception if an error
    #  occurs.
    #  if an exception does not occur, implementation should always return an
    #  object of type common.writable.balances.Balances
    def visit( self, obj ):
        b = Balances()
        b.addBalance( 'test-balance', 1.0 )
        return b