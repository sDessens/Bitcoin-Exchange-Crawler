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
import common.writeable.partialBalance
import common.writeable.file

def getInstance():
    return LocalFileWriteVisitor()


class LocalFileWriteVisitor:
    def __init__(self):
        pass

    def accept( self, json, obj ):
        try:
            return (json['type'] == 'localfile') and\
                    any([ isinstance(obj, common.writeable.file.File),
                          isinstance(obj, common.writeable.partialBalance.PartialBalance) ])
        except Exception as e:
            return False

    def visit( self, json, obj ):
        storage = LocalFileStorage.LocalFileStorage(json['folder'])

        if isinstance( obj, common.writeable.file.File ):
            for k, v in obj.items():
                storage.writeFile( k, v )
        elif isinstance( obj, common.writeable.partialBalance.PartialBalance ):
            for k, v in obj.items():
                print k, v
                storage.writeBalance( k, v )
