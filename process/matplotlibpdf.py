#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is implementation of an process visitor that exports data
#               to PDF format using the matplotlib library.
#
# Author:       Stefan Dessens
#
# Created:      18-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

from common.writeable.file import File
from common.writeable.fullBalance import FullBalance
import common.balanceData
import common.tempFileLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import logging
log = logging.getLogger( 'main.process.matplotlibpdf' )

## This function is required for every Visitor module
def getInstance():
    return MatplotlibVisitor()

## this is a stub Process visitor. It provides an template that provides
#  all required functionality for an Process visitor
class MatplotlibVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'matplotlibpdf'
        except Exception as e:
            return False

    ## run the process algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  may return exception
    def visit( self, json, resources ):
        tmpfile = common.tempFileLib.generateTempFile(True)

        plotter = MatplotlibPdfWrapper( tmpfile )
        for view in json['views']:
            try:
                plotter.addView( view, resources )
            except Exception as e:
                log.error( str(e) )
        plotter.finalize()

        resources[ json['target'] ] = File( tmpfile )
        return resources

class MatplotlibPdfWrapper:
    ## create new matplotlib wrapper. This is a convinient class
    #  to create a pdf page with multiple pages.
    def __init__(self, filename = 'all.pdf' ):
        self._pdf = PdfPages( filename )

    ## add a view to the existing pdf page
    #  @param json block of data that contains options.
    #  @param resources array of common.writable.*
    #  @return nothing, but mutates internal state
    def addView(self, json, resources):
        title = json['title']
        sources = json['source']
        days = json['days'] if 'days' in json else None

        log.info( 'plotting {0}'.format(title) )

        objects = []

        for key in json['source']:
            if key not in resources:
                log.error( 'attempting to plot resource {0}, but no such resource exists'.format(key) )
                continue
            resource = resources[key]
            if isinstance( resource, FullBalance ):
                objects.append( (key, resource.value) )
            else:
                log.error( 'attempting to plot resource {0}, but is of unsupported type {1}'
                           .format( key, resource.__class__.__name__ ) )

        type = json['type'] if 'type' in json else 'default'

        if len(objects) == 0:
            log.error( 'skipping plot titled {0} because there are no objects to plot...'.format( title ) )
            return

        if type == 'default':
            self._raw_plot_line( title, objects, days )
        elif type == 'stacked':
            self._raw_plot_stacked( title, objects, days )
        else:
            log.error( 'unknown plot type {0}'.format(type) )

    ## save and close the plot.
    #  implementation must call this function, or a memory leak will occur.
    def finalize(self):
        self._pdf.close()
        plt.close()

    ## plot the specified data
    #  @param the title of the plot
    #  @param objects an array of (name, BalanceData)
    #  @param days (optional) the Y width of the plot in days
    def _raw_plot_line(self, title, objects, days = None):
        fig, ax = plt.subplots()
        fig.set_figheight(12)   # inches..
        fig.set_figwidth(20)

        ax.set_title(title, fontsize=18)

        # find the end of this plot
        maxTimestamp = max( [ balance.maxTimestampAsDateTime() for key, balance in objects ] )

        for key, balance in objects:
            ax.plot( balance.timestampsAsDateTime(), balance.balance(), label=key )
            ax.annotate( ' ' + key, xy=( maxTimestamp, balance.interpolate( maxTimestamp ) ) )

        ax.grid(True)
        if days is not None and len(objects):
            ax.set_xlim( [ maxTimestamp - datetime.timedelta(days=days) ], maxTimestamp )

        self._pdf.savefig( bbox_inches='tight', dpi=160 )

    def _raw_plot_stacked(self, title, objects, days = None):
        fig, ax = plt.subplots()
        fig.set_figheight(12)   # inches..
        fig.set_figwidth(20)

        ax.set_title(title, fontsize=18)

        # generate a sum of all balances. This neatly generated all unique X points
        summed = common.balanceData.sum( [ o for k, o in objects ] )
        X = summed.timestampAsUnix()

        # find the end of this plot
        maxTimestamp = summed.maxTimestampAsDateTime()

        alpha = 1.0

        """
        floor = [0]*len(summed)
        for key, balance in objects:
            ceiling = [  floor[i] + balance.interpolate(X[i]) for i in range(len(floor)) ]
            plt.fill_between( summed.timestampsAsDateTime(),
                              floor, ceiling,
                              alpha=alpha, )
            ax.plot( summed.timestampsAsDateTime(), ceiling, color='k' )
            alpha = alpha / 1.3
            ax.annotate( ' ' + key, xy=( maxTimestamp, (floor[-1] + ceiling[-1]) / 2.0 ) )
            floor = ceiling
        """


        ceilings = []
        floor = 0
        for key, balance in objects:
            ceiling = [  balance.interpolate(X[i]) for i in range(len(X)) ]
            ax.annotate( ' ' + key, xy=( maxTimestamp, floor + ceiling[-1] / 2.0 ) )
            ceilings.append(ceiling)
            floor = floor + ceiling[-1]

        plt.stackplot( summed.timestampsAsDateTime(), ceilings, baseline="zero" )


        ax.grid(True)
        if days is not None and len(objects):
            ax.set_xlim( [ maxTimestamp - datetime.timedelta(days=days) ], maxTimestamp )

        self._pdf.savefig( bbox_inches='tight', dpi=160 )


