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
from common.writeable.fullBalance import FullBalance
from common.writeable.collection import Collection


def getInstance():
    return LocalFileReadVisitor()


##
# this is a LocalFileReadVisitor. It provides a way to read balance from a localfile
class LocalFileReadVisitor:
    def __init__(self):
        pass

    ## check if given object is accepted by visitor
    #  @return True if this visitor accepts the given object.
    def accept( self, json ):
        try:
            return json['type'] == 'localfile'
        except Exception as e:
            return False

    ## parse and return data specified in obj.
    #  @return common.writable.collection
    #  may throw an exception
    def visit(self, json):
        storage = LocalFileStorage( json['folder'] )
        out = Collection()

        for id in json['data']:
            try:
                out[id] = FullBalance( storage.readBalance(id) )
            except Exception as e:
                print str(e)
        return out
