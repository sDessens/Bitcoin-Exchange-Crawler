# this module can be used to write various resource to the local file system.


from common.localFileStorageLib import LocalFileStorage
from common.resources.fullBalance import FullBalance
import logging
log = logging.getLogger( 'main.read.localfile' )


##
# this is a LocalFileReadVisitor. It provides a way to read balance from a localfile
class LocalFileBalanceHistory:
    def __init__(self, folder):
        self._folder = folder

    def visit(self, name):
        storage = LocalFileStorage(self._folder)
        return storage.readBalance(name)
