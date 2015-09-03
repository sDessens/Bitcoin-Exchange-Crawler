# this module allows to write various resource to the local file system

import logging
import common.localFileStorageLib as LocalFileStorage

log = logging.getLogger( 'main.write.localfile' )


class LocalFileWriteVisitor:
    def __init__(self, folder):
        self._folder = folder

    def visit(self, name, value):
        storage = LocalFileStorage.LocalFileStorage(self._folder)

        storage.writeBalance(name, value)
