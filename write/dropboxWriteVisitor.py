import json
import tempfile
import os
import time

import common.dropboxLib as db
import common.writeable.partialBalance
import common.writeable.file


def getInstance():
    return DropboxStorageVisitor()

class DropboxStorageVisitor:
    def __init__(self):
        pass

    def accept( self, json, obj ):
        try:
            return (json['type'] == 'dropbox') and\
                    any([ isinstance(obj, common.writeable.file.File),
                          isinstance(obj, common.writeable.partialBalance.PartialBalance) ])
        except Exception as e:
            return False

    def visit( self, json, obj ):
        #storage = db.DropboxStorage(json['folder'], json['app_key'], json['app_secret'] )
        storage = db.DropboxStorage('/mercurytradingsystems')
        storage.writeBalance('test-troep',23123213)
        return

        if isinstance( obj, common.writeable.file.File ):
            for k, v in obj.items():
                storage.writeFile( k, v )
        elif isinstance( obj, common.writeable.partialBalance.PartialBalance ):
            for k, v in obj.items():
                print k, v
                storage.writeBalance( k, v )