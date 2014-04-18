#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is implementation of an export visitor that exports data
#               to PDF format using the matplotlib python library.
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime


## This function is required for every Visitor module
def getInstance():
    return MatplotlibVisitor()

## this is a stub Export visitor. It provides an template that provides
#  all required functionality for an Export visitor
class MatplotlibVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'matplotlibpdf'
        except Exception as e:
            return False

    ## run the export algorithm.
    #  this export algorithm writes all data to pdf as specified in json.
    #  @param data an {'identifier' : BalanceData} map.
    #  @param json contains implementation defined information about the export type
    #  @return some sort of file array
    def visit( self, json, data, writedb ):
        tmpfile = 'matplotlibpdf.tmp.pdf'

        plotter = MatplotlibPdfWrapper( tmpfile )

        for view in json['views']:
            plotter.addView( view, data )

        plotter.finalize()

        print writedb

        try:
            json['write']
        except:
            raise Exception('unable to write pdf because no key ''write'' exists in json' )

        writter = None
        try:
            writter = writedb[json['write']]
        except:
            raise Exception('could not find writter', json['write'])

        writter.uploadFile( tmpfile, json['folder'], True )

        return []


class MatplotlibPdfWrapper:
    ## create new matplotlib wrapper. This is a convinient class
    #  to create a pdf page with multiple pages.
    def __init__(self, filename = 'all.pdf' ):
        self._pdf = PdfPages( filename )

    ## add a view to the existing pdf page
    #  @param json block of data that contains options.
    #  @param data an {'identifier' : BalanceData} map.
    #  @return nothing, but mutates internal state
    def addView(self, json, data):
        title = json['title']
        sources = json['source']
        days = json['days'] if 'days' in json else None

        print 'plotting', title, 'from sources', sources
        self._raw_plot( title, sources, days, data )

    ## save and close the plot.
    #  implementation must call this function, or a memory leak will occur.
    def finalize(self):
        self._pdf.close()
        plt.close()


    def _raw_plot(self, title, sources, days, data):
        fig, ax = plt.subplots()
        fig.set_figheight(12)   # inches..
        fig.set_figwidth(20)

        ax.set_title(title, fontsize=18)

        objects = dict( [ (id, data[id]) for id in sources ] )

        if len( objects ) == 0:
            raise Exception( 'plot with zero objects???' )

        # find the end of this plot
        maxTimestamp = max( [ val.maxTimestampAsDateTime() for key,val in objects.items() ] )

        for key, val in objects.items():
            ax.plot( val.timestampsAsDateTime(), val.balance(), label=key )
            ax.annotate( ' ' + key, xy=( maxTimestamp, val.interpolate( maxTimestamp ) ) )

        ax.grid(True)
        if days is not None:
            ax.set_xlim( [ maxTimestamp - datetime.timedelta(days=days) ], maxTimestamp )

        self._pdf.savefig( bbox_inches='tight', dpi=160 )


