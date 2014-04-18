#-------------------------------------------------------------------------------
# Name          read
# Purpose:      read data from various exchanges, specified in (by default)
#               readconfig.json. data is then written to db.
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import json
import common.parsevisitorsfromfolder as pv
# dynamic import of all modules in folder exchanges/*
# dynamic import of all modules in folder writedb/*


def main():
    exchangeVisitors = pv.getVisitorsFromFolder( 'exchanges' )
    storageVisitors = pv.getVisitorsFromFolder( 'writedb' )

    # get contents of config file
    config = json.load( open( 'readconfig.json', 'r' ) )

    storageVisitor = storageVisitors.select( config['storage'] )
    if storageVisitor is None:
        raise Exception( 'unable to derive storage manager from config file' )
    else:
        storageManager = storageVisitor.visit( config['storage'] )

    for section in config['exchanges']:
        visitor = exchangeVisitors.select( section )
        if visitor is not None:
            try:
                info = visitor.visit( section )
                storageManager.writeBalance( section['name'], info )
            except Exception as e:
                print str(e)
        else:
            print 'no visitor could be found that accepts', section

if __name__ == '__main__':
    main()
