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

def getInstance():
    return DropboxReadVisitor()

##
# this is a stub db reader. It provides an template that provides all
# required functionality for an db reader
class DropboxReadVisitor:
    def __init__(self):
        pass

    ##
    # @return True if this visitor accepts the given object.
    def accept( self, obj ):
        try:
            return obj['type'] == 'dropbox'
        except Exception as e:
            return False

    ##parse and return data specified in obj.
    # @return 'identifier' -> BalanceData map or exception.
    def visit(self, obj):
        storage = db.DropboxStorage( obj['folder'],obj['separator'], obj['app_key'], obj['app_secret'] )

        out = {}
        for id in obj['data']:
            try:
                out[id] = storage.read(id)
            except Exception as e:
                print str(e)
        return out
