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
from common.resources.partialBalance import PartialBalance
from common.resources.file import File
import logging
log = logging.getLogger( 'main.write.localfile' )


def getInstance():
    return LocalFileWriteVisitor()


class LocalFileWriteVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'localfile'
        except Exception as e:
            return False

    def visit( self, json, resources ):
        storage = LocalFileStorage.LocalFileStorage(json['folder'])

        for key in json['data']:
            if key not in resources:
                log.error( 'attempting to write resource {0}, but no such resource exists'.format(key) )
                continue
            resource = resources[key]
            if isinstance( resource, PartialBalance ):
                storage.writeBalance(key, resource.value)
            elif isinstance( resource, File ):
                storage.writeFile( resource.filename, key )
            else:
                log.error( 'attempting to write resource {0}, but is of unsupported type {1}'
                           .format( key, resource.__class__.__name__ ) )
