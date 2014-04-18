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
import logging

##scan target folder for all modules that implement the
# getInstance() function
# @param moduleName name of the folder to query
# @return visitorPattern object
def getVisitorsFromFolder( moduleName ):
    log = logging.getLogger('main.visitor')

    visitors = visitorpattern.VisitorPattern()

    for item in __import__(moduleName).__all__:
        try:
            module = __import__( moduleName + '.' + item )
            attr = getattr( module, item )
            try:
                visitors.addVisitor( attr.getInstance() )
                log.info( 'added visitor {0}/{1}'.format( moduleName, item ) )
            except Exception as e:
                if type(e) is AssertionError:
                     log.error( '{0}.py: {1}'.format(item, str(e) ) )
                else:
                    log.error( '{0}.py: unable to add exchange visitor.'.format( item ) )
        except ImportError as e:
            log.error( 'unable to add visitor {0}/{1} because: {2}'.format( moduleName, item, str(e) ) )

    return visitors
