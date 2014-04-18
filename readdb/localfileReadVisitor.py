#-------------------------------------------------------------------------------
# Name          LocalFileReadBalanceVisitor
# Purpose:      Module is localfile storage balance implementation of ReadDB Visitor.
#
# Author:       Jasper van Gelder
#
# Created:      18-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

from common.localFileStorageLib import LocalFileStorage
def getInstance():
    return LocalFileReadBalanceVisitor()

##
# this is a LocalFileReadVisitor. It provides a way to read balance from a localfile
class LocalFileReadBalanceVisitor:
    def __init__(self):
        pass

    ## check if given object is accepted by visitor
    #  @return True if this visitor accepts the given object.
    def accept( self, obj ):
        try:
            return obj['type'] == 'localstoragebalance'
        except Exception as e:
            return False

    ## parse and return data specified in obj.
    #  @return {'identifier' : BalanceData} map or exception.
    def visit(self, obj):
        storage = LocalFileStorage( obj['folder'],obj['separator'] )

        out = {}
        for id in obj['data']:
            try:
                out[id] = storage.readBalance(id)
            except Exception as e:
                print str(e)
        return out
