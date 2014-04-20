import json
import tempfile
import os
import time

import common.dropboxLib as db
import common.writeable.balances
import common.writeable.files


def getInstance():
    return DropboxStorageVisitor()

class DropboxStorageVisitor:
    def __init__(self):
        pass

    def accept( self, json, obj ):
        try:
            return (json['type'] == 'dropbox') and\
                    any([ isinstance(obj, common.writeable.files.Files),
                          isinstance(obj, common.writeable.balances.Balances) ])
        except Exception as e:
            return False

    def visit( self, json, obj ):
        #storage = db.DropboxStorage(json['folder'], json['app_key'], json['app_secret'] )
        storage = db.DropboxStorage('/mercurytradingsystems','x989ou22sjzmped','x6aqsrhk47jp5r3')
        storage.writeBalance('test-troep',23123213)
        return

        if isinstance( obj, common.writeable.files.Files ):
            for k, v in obj.items():
                storage.writeFile( k, v )
        elif isinstance( obj, common.writeable.balances.Balances ):
            for k, v in obj.items():
                print k, v
                storage.writeBalance( k, v )
