#-------------------------------------------------------------------------------
# Name          parseVisitorsFromFolder
# Purpose:      Module that allows dynamic loading of libraries from a folder
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------


import visitorpattern

def getVisitorsFromFolder( moduleName ):
    visitors = visitorpattern.VisitorPattern()

    for item in __import__(moduleName).__all__:
        module = __import__( moduleName + '.' + item )
        attr = getattr( module, item )
        try:
            visitors.addVisitor( attr.getInstance() )
            print 'added visitor {0}/{1}'.format( moduleName, item )
        except Exception as e:
            if type(e) is AssertionError:
                 print '{0}.py:'.format(item), str(e)
            else:
                print '{0}.py: unable to add exchange visitor.'.format( item )

    return visitors
