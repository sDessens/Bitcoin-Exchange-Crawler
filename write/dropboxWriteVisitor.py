# Module allows writting stuff to dropbox based database system

import logging
import common.dropboxLib as db

log = logging.getLogger( 'main.write.dropbox' )


class DropboxAppendBalance:
    def __init__(self, folder):
        self._folder = folder

    def visit(self, name, value):
        storage = db.DropboxStorage(self._folder)
        storage.writeBalance(name, value)
