# Module is stub implementation of Read Visitor.
# Developers can use this file as an example when implementing
# additional information sources


import common.dropboxLib as db
from common.resources.fullBalance import FullBalance
from common.resources.collection import Collection
from multiprocessing import Pool
import logging
log = logging.getLogger( 'main.read.dropbox' )

def getInstance():
    return DropboxReadVisitor()

##
# this is a DropboxReadVisitor. It provides a way to read a file from dropbox
class DropboxReadVisitor:
    def __init__(self):
        pass

    ## check if given object is accepted by visitor
    #  @return True if this visitor accepts the given object.
    def accept( self, json ):
        try:
            return json['type'] == 'dropbox'
        except Exception as e:
            return False

    ## parse and return data specified in obj.
    #  @return {'identifier' : BalanceData} map or exception.

    def visit(self, json):
        storage = db.DropboxStorage( json['folder'] )
        out = Collection()
        pool = Pool(processes=len(json['data']))

        instances = []

        for id in json['data']:
            log.info( 'kicking thread to read {0}'.format( id ) )
            instances.append( DropboxReadAsync( id, storage, pool ) )

        for instance in instances:
            try:
                out[instance.name] = FullBalance( instance.get() )
            except Exception as e:
                log.error( 'an exception has occured when reading {0}'.format( instance.name ) )


        """ single threaded version
        for id in json['data']:
            try:
                out[id] = FullBalance( storage.readBalance(id) )
                log.info( 'downloaded {0}'.format(id) )
            except Exception as e:
                if len(str(e)):
                    print str(e)
        """

        return out

def f( instance, name ):
    return instance.readBalance(name)

class DropboxReadAsync():
    def __init__(self, name, dropboxStorageInstance, pool):
        self.name = name
        self.async = pool.apply_async( func=f, args=(dropboxStorageInstance, name) )

    def get(self):
        self.async.wait()
        return self.async.get()