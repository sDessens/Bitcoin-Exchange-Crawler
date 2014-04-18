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
import common.parsevisitorsfromfolder as pv
# dynamic import of all modules in folder export/*
# dynamic import of all modules in folder readdb/*
# dynamic import of all modules in folder postprocess/*


def main():
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
            print 'unable to find import visitor for section', section

    for section in config['postprocess']:
        vis = processVisitors.select( section )
        if vis is not None:
            data =  vis.visit( section, balances )
        else:
            print 'unable to find postprocess visitor for section', section

    print 'got balances for', balances.keys()

    storageManagers = {}
    for k, section in config['write'].items():
        vis = writeVisitors.select( section )
        if vis is not None:
            storageManagers[k] = vis.visit( section )
        else:
            print 'unable to find writedb visitor for section', section


    for section in config['export']:
        vis = exportVisitors.select( section )
        if vis is not None:
            vis.visit( section, balances, storageManagers )
        else:
            print 'unable to find export visitor for section', section

    # todo write stuff to file

if __name__ == '__main__':
    main()
