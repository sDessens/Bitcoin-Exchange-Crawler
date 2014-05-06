# this module defined the base class of all resoures,
# and an 'resource manager' class.




# baseclass of all resource
class Resource:
    pass

class Collection( dict ):
    def __setitem__(self, key, value):
        assert issubclass( value.__class__, Resource )
        super( Collection, self ).__setitem__( key, value )

    ## select an subset of resources
    #  @param selector. If plain string, select resource(s) with that identifier.
    #  otherwise, interprent argument as array of strings, add resource in OR fashion.
    #  @param mustBeType (optional) select only resources of that type.
    #  @return an (key, resource) array of matched items. May return empty array if nothing matched.
    def selectMany(self, selector, mustBeType=Resource):
        assert( isinstance( mustBeType, Resource) )
        out = []

        if isinstance( selector, str ):
            for k, v in self.items():
                if isinstance( v, mustBeType ) and self._matches( k, selector ):
                    out.append((k, v))
        else:
            for k, v in self.items():
                if isinstance( v, mustBeType ):
                    for sel in selector:
                        if self._matches( k, sel ):
                            out.append((k, v))
                            break

        return out

    ## select one resource
    #  @param selector string
    #  @param mustBeType (optional) the type of the resouce
    #  @return the resource, of none if it did not exist of is of incorrect type
    def selectOne(self, selector, mustBeType=Resource):
        assert( isinstance( mustBeType, Resource) )
        try:
            res = self.__getitem__(selector)
            if isinstance(res, mustBeType):
                return res
        except Exception as e:
            pass
        return None

    def _matches(self, id, selector):
        if id == selector:
            return True
        return False

    def report(self, msg = None):
        if msg is not None:
            print msg

        for id in set( [ v.__class__ for k, v in set( self.items() ) ] ):
            for k, v in self.items():
                if v.__class__ == id:
                    print '    {0:15s} => {1}'.format( k, str(v) )
