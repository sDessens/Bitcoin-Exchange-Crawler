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

import common.dropboxLib as db
import logging
log = logging.getLogger( 'main.dropbox' )

def getInstance():
    return DropboxReadVisitor()

##
# this is a DropboxReadVisitor. It provides a way to read a file from dropbox
class DropboxReadVisitor:
    def __init__(self):
        pass

    ## check if given object is accepted by visitor
    #  @return True if this visitor accepts the given object.
    def accept( self, obj ):
        try:
            return obj['type'] == 'dropbox'
        except Exception as e:
            return False

    ## parse and return data specified in obj.
    #  @return {'identifier' : BalanceData} map or exception.
    def visit(self, obj):
        storage = db.DropboxStorage( obj['folder'] )

        out = {}
        for id in obj['data']:
            try:
                out[id] = storage.readBalance(id)
                log.info( 'downloaded {0}'.format(id) )
            except Exception as e:
                if len(str(e)):
                    print str(e)
        return out
