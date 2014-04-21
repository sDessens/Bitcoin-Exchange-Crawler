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
    return StubReadVisitor()

## this is a stub db reader. It provides an template that provides all
#  required functionality for an db reader
class StubReadVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object.
    #  @return true if object is accepted
    #  May not throw exceptions.
    def accept( self, json ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    ## parse and return data specified in json.
    #  @return common.writable.collection
    #  may throw an exception
    def visit( self, json ):
        return []