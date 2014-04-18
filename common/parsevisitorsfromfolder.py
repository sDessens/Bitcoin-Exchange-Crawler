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

##scan target folder for all modules that implement the
# getInstance() function
# @param moduleName name of the folder to query
# @return visitorPattern object
def getVisitorsFromFolder( moduleName ):
    visitors = visitorpattern.VisitorPattern()

    for item in __import__(moduleName).__all__:
        try:
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
        except ImportError as e:
            print 'unable to add visitor {0}/{1} because: {2}'.format( moduleName, item, str(e) )

    return visitors
