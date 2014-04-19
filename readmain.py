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

    storageSection = config['storage']

    for section in config['exchanges']:
        visitor = exchangeVisitors.select( section )
        if visitor is not None:
            try:
                balance = visitor.visit( section )
                try:
                    visitor = storageVisitors.select( storageSection, balance )
                    if visitor is not None:
                        try:
                            visitor.visit( storageSection, balance )
                        except Exception as e:
                            raise
                            log.error( 'an exception occured when visiting {0}: {1}'.format(
                                visitor.__class__.__name__, str(e) ) )
                    else:
                        log.error( 'unable to find write visitor for class {0}, section {1}'
                                   .format( balance.__class__.__name__, storageSection )  )
                except Exception as e:
                    raise
                    log.error( 'an exception occurred when searching for write visitor of section {0}: {1}'
                               .format( storageSection, str(e) ) )

            except Exception as e:
                raise
                log.error( 'an exception occurred in visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )
        else:
            log.error( 'no visitor could be found that accepts section {0}'.format( section ) )

if __name__ == '__main__':
    main()
