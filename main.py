#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Stefan
#
# Created:     15-04-2014
# Copyright:   (c) Stefan 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json

import visitorpattern
# dynamic import of all modules in folder exchanges/
# dynamic import of all modules in folder ?????/

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


def main():
    exchangeVisitors = getVisitorsFromFolder( 'exchanges' )
    #storageVisitors = getVisitorsFromFolder( 'storage' )

    # get contents of config file
    config = json.load( open( 'config.json', 'r' ) ) #todo get config file contents

    """
    storageManager = storageVisitors.select( config['storage'] )
    if storageManager == None:
        raise Exception( 'unable to derive storage manager from config file' )
    else:
        storageManager = storageManager.visit( config )
    """

    for section in config['exchanges']:
        visitor = exchangeVisitors.select( section )
        if visitor != None:
            try:
                info = visitor.visit( section )
                print info
                #storageManager.write( info, section )
            except Exception as e:
                print str(e)
        else:
            print 'no visitor could be found that accepts', section

if __name__ == '__main__':
    main()
