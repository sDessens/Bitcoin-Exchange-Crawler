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
from common.writeable.collection import Collection
# dynamic import of all modules in folder exchanges/*
# dynamic import of all modules in folder writedb/*


def main():
    #FORMAT = "%(asctime)-15s %(levelname)s %(name)s: %(message)s"
    FORMAT = "%(levelname)s\t%(name)s: %(message)s"
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger('main')
    log.setLevel(logging.DEBUG)


    readVisitors = pv.getVisitorsFromFolder( 'read' )
    exportVisitors = pv.getVisitorsFromFolder( 'export' )
    writeVisitors = pv.getVisitorsFromFolder( 'write' )

    resources = Collection()

    # get contents of config file
    config = json.load( open( 'readconfig.json', 'r' ) )

    for section in config['read']:
        visitor = readVisitors.select( section )
        if visitor is None:
            log.error( 'no read visitor could be found for section {0}'.format( section ) )
            continue
        try:
            resources.update( visitor.visit( section ) )
        except Exception as e:
            log.error( 'an exception occurred when visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )

    resources.report('after reading, the available resources are:')


    for section in config['export']:
        visitor = exportVisitors.select( section )
        if visitor is None:
            log.error( 'no export visitor could be found for section {0}'.format( section ) )
            continue
        try:
            resources.update( visitor.visit( section, resources ) )
        except Exception as e:
            log.error( 'an exception occurred when visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )

    resources.report('after exporting, the available resources are:')


if __name__ == '__main__':
    main()
