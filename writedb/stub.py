#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of WriteDB Visitor.
#               Developers can use this file as an example when implementing
#               additional write db's.
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import common.balanceData as balanceData


def getInstance():
    return StubWriteVisitor()


## this is a stub write visitor. It provides an template that provides all
#  required functionality for an storage visitor
class StubWriteVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, obj ):
        try:
            return obj['type'] == 'stub'
        except Exception as e:
            return False

    ##
    #  @return some object with read and write functions
    def visit(self, obj):
        return StubWritter()


class StubWritter:
    def __init__(self):
        pass;

    ## The write function appends given value to to the data
    #  @param identifier an string that uniquely identifies the target
    #  @param value the value that should be writen
    def writeBalance(self, identifier, value):
        print 'StubStorage: write value', value, 'to', identifier

    def uploadFile(self, path, uploadPath, overwrite):
        print 'StubStorage: write file', path, 'to', uploadPath, '(overwrite =', overwrite, ')'
        pass
