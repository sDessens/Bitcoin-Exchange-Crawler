import json
import tempfile
import os
import time

import common.dropboxLib as db

def getInstance():
    return DropboxStorageVisitor()

class DropboxStorageVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'dropboxstorage'
        except Exception as e:
            return False

    def visit( self, obj ):
        return db.DropboxStorage(obj['folder'],obj['separator'], obj['app_key'], obj['app_secret'] )