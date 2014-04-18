#-------------------------------------------------------------------------------
# Name          write
# Purpose:      Import data from db and other various sources,  as specified in
#               (by default) writeconfig.json. Data is then exported to the
#               specified format (e.g. pdf, svg) and written to a file.
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
# dynamic import of all modules in folder export/*
# dynamic import of all modules in folder readdb/*
# dynamic import of all modules in folder postprocess/*



def main():
    FORMAT = "%(asctime)-15s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger('main')
    log.setLevel(logging.INFO)


    readVisitors = pv.getVisitorsFromFolder( 'readdb' )
    writeVisitors = pv.getVisitorsFromFolder( 'writedb' )
    processVisitors = pv.getVisitorsFromFolder( 'postprocess' )
    exportVisitors = pv.getVisitorsFromFolder( 'export' )

    # get contents of config file
    config = json.load( open( 'writeconfig.json', 'r' ) )

    balances = {} # map of {'identifier' : BalanceData}



    for section in config['import']:
        vis = readVisitors.select( section )
        if vis is not None:
            balances.update( vis.visit( section ) )
        else:
            log.error( 'unable to find import visitor for section {0}'.format(section) )

    for section in config['postprocess']:
        vis = processVisitors.select( section )
        if vis is not None:
            balances =  vis.visit( section, balances )
        else:
            log.error( 'unable to find post-process visitor for section {0}'.format(section) )

    log.debug( 'got balances for {0}'.format( balances.keys() ) )

    storageManagers = {}
    for k, section in config['write'].items():
        vis = writeVisitors.select( section )
        if vis is not None:
            storageManagers[k] = vis.visit( section )
        else:
            log.error( 'unable to find writedb visitor for section {0}'.format(section) )


    for section in config['export']:
        vis = exportVisitors.select( section )
        if vis is not None:
            vis.visit( section, balances, storageManagers )
        else:
            log.error( 'unable to find export visitor for section {0}'.format(section) )


if __name__ == '__main__':
    main()
