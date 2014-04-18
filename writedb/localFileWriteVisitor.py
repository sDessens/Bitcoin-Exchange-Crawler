#-------------------------------------------------------------------------------
# Name          LocalFileStorageVisitor
# Purpose:      Module is Local File Storage implementation of WriteDB Visitor.

# Author:       Jasper van Gelder
#
# Created:      17-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------
import common.localFileStorageLib as LocalFileStorage

def getInstance():
    return LocalFileWriteVisitor()

class LocalFileWriteVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'localfile'
        except Exception as e:
            return False

    def visit( self, obj ):
        storage = LocalFileStorage.LocalFileStorage(obj['folder'])
        return storage