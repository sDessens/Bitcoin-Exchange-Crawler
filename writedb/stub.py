#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of WriteDB Visitor.
#               Developers can use this file as an example when implementing
#               additional writeable objects
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import common.writeable.singleDatapoint
import common.writeable.files

def getInstance():
    return StubWriteVisitor()


## this is a stub write visitor. It provides an template that provides all
#  required functionality for an storage visitor
class StubWriteVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json, obj ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    ## write the object to the storage specified in json
    #  or throw exception if something goes wrong.
    #  obj is always of type common.writeable.*
    def visit(self, json, obj):
        if isinstance( obj, common.writeable.singleDatapoint.SingleDatapoint ):
            print 'StubWritter: writting balances:', obj
        elif isinstance( obj, common.writeable.files.Files ):
            print 'stubwritter: writting files:', obj
        else:
            print 'stubWritter: writting unknwon object', obj.__class__.__name__, obj
