#-------------------------------------------------------------------------------
# Name          main
# Purpose:      Module that manages the entire exchange balance crawing process.
#               Various Exchange and Storage visitors are initialized from
#               the subfolders /exchanges/ and /storage/, which specify
#               what type of information gets crawled and stored.
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import json
import parsevisitorsfromfolder as pv
# dynamic import of all modules in folder exchanges/*
# dynamic import of all modules in folder storage/*


def main():
    exchangeVisitors = pv.getVisitorsFromFolder( 'exchanges' )
    storageVisitors = pv.getVisitorsFromFolder( 'storage' )

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
                storageManager.write( section['name'], info )
            except Exception as e:
                print str(e)
        else:
            print 'no visitor could be found that accepts', section

if __name__ == '__main__':
    main()
