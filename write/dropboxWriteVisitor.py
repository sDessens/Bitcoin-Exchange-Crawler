#-------------------------------------------------------------------------------
# Name          DropboxWriteVisitor
# Purpose:      Module allows writting stuff to dropbox based database system
#
# Author:       Stefan Dessens
#
# Created:      21-04-2014
# Copyright:    (c) Stefan Dessens
# Licence:      TBD
#-------------------------------------------------------------------------------


import json
import tempfile
import os
import time

import common.dropboxLib as db
from common.writeable.partialBalance import PartialBalance
from common.writeable.file import File

import logging
log = logging.getLogger( 'main.write.dropbox' )


def getInstance():
    return DropboxStorageVisitor()

class DropboxStorageVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'dropbox'
        except Exception as e:
            return False

    def visit( self, json, resources ):
        storage = db.DropboxStorage(json['folder'])

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
