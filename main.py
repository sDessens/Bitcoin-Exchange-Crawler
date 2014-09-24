#-------------------------------------------------------------------------------
# Name          main
# Purpose:      Read, process, and write various objects, as specified in an
#               json config file.
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import json
import logging
import common.parsevisitorsfromfolder as pv
from common.resources.collection import Collection
import traceback
import argparse
import traceback
# dynamic import of all modules in folder read/*
# dynamic import of all modules in folder process/*
# dynamic import of all modules in folder write/*


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-c", "--config-file", help='Set config file path (default config.json)',
                         default='config.json', type=str )
    parser.add_argument( "-l", "--log-level", help="Set log level. 10=debug 20=info 30=warn 40=error (default 20)",
                         default=20, type=int)
    arguments = parser.parse_args()

    FORMAT = "%(levelname)s\t%(name)s: %(message)s"
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger('main')
    log.setLevel(arguments.log_level)


    readVisitors = pv.getVisitorsFromFolder( 'read' )
    processVisitors = pv.getVisitorsFromFolder( 'process' )
    writeVisitors = pv.getVisitorsFromFolder( 'write' )

    resources = Collection()

    # get contents of config file
    config = json.load( open( arguments.config_file, 'r' ) )

    for section in config['read']:
        visitor = readVisitors.select( section )
        if visitor is None:
            log.error( 'no read visitor could be found for section {0}'.format( section ) )
            continue
        try:
            resources.update( visitor.visit( section ) )
        except Exception as e:
            log.error( 'an exception occurred when visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )
            log.debug(traceback.format_exc())

    resources.report('after reading, the available resources are:')

    for section in config['process']:
        visitor = processVisitors.select( section )
        if visitor is None:
            log.error( 'no process visitor could be found for section {0}'.format( section ) )
            continue
        try:
            resources.update( visitor.visit( section, resources ) )
        except Exception as e:
            log.error( 'an exception occurred when visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )
            log.debug(traceback.format_exc())

    resources.report('after processing, the available resources are:')

    for section in config['write']:
        visitor = writeVisitors.select( section )
        if visitor is None:
            log.error( 'no write visitor could be found for section {0}'.format( section ) )
            continue
        try:
            visitor.visit( section, resources )
        except Exception as e:
            log.error( 'an exception occurred when visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )
            log.debug(traceback.format_exc())

if __name__ == '__main__':
    main()
    exit(0)
