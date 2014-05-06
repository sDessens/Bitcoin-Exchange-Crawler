# this module can be used to write various resource to the local file system.


from common.localFileStorageLib import LocalFileStorage
from common.resources.fullBalance import FullBalance
from common.resources.collection import Collection
import logging
log = logging.getLogger( 'main.read.dropbox' )


def getInstance():
    return LocalFileReadVisitor()


##
# this is a LocalFileReadVisitor. It provides a way to read balance from a localfile
class LocalFileReadVisitor:
    def __init__(self):
        pass

    ## check if given object is accepted by visitor
    #  @return True if this visitor accepts the given object.
    def accept( self, json ):
        try:
            return json['type'] == 'localfile'
        except Exception as e:
            return False

    ## parse and return data specified in obj.
    #  @return common.writable.collection
    #  may throw an exception
    def visit(self, json):
        storage = LocalFileStorage( json['folder'] )
        out = Collection()

        for id in json['data']:
            try:
                out[id] = FullBalance( storage.readBalance(id) )
            except Exception as e:
                log.error(str(e))
        return out
