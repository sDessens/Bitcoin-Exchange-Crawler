# baseclass of all resource
class Resource:
    pass

class Collection( dict ):
    def __setitem__(self, key, value):
        assert isinstance( value, Resource )
        super( Collection, self ).__setitem__( key, value )

    def report(self, msg = None):
        if msg is not None:
            print msg

        for id in set( [ v.__class__ for k, v in set( self.items() ) ] ):
            for k, v in self.items():
                if v.__class__ == id:
                    print '    {0:15s} => {1}'.format( k, str(v) )


