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
import logging
import common.parsevisitorsfromfolder as pv
# dynamic import of all modules in folder exchanges/*
# dynamic import of all modules in folder writedb/*


def main():
    FORMAT = "%(asctime)-15s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger('main')
    log.setLevel(logging.DEBUG)


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
                log.error( 'an exception occured in visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )
        else:
            log.error( 'no visitor could be found that accepts section {0}'.format( section ) )

if __name__ == '__main__':
    main()
