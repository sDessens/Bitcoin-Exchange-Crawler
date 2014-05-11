# Module implements an  process visitor that exports data
# to PDF format using the matplotlib library.


from common.resources.file import File
from common.resources.fullBalance import FullBalance
import common.balanceData
import common.tempFileLib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import logging
import traceback
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
                log.error( "an exception occured during plotting" )
                log.debug( traceback.format_exc() )
        plotter.finalize()

        resources[ json['out'] ] = File( tmpfile )
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
        type = json['type'] if 'type' in json else 'line'
        sources = json['source']
        days = json['days'] if 'days' in json else None

        log.info( 'plotting {0}'.format(title) )

        objects = []

        for key in sources:
            res = resources.selectOne(key)
            if key is None:
                log.error( 'attempting to plot resource {0}, but no such resource exists'.format(key) )
            elif isinstance( res, FullBalance ):
                objects.append( (key, res.value) )
            else:
                log.error( 'attempting to plot resource {0}, but is of unsupported type {1}'
                           .format( key, res.__class__.__name__ ) )

        if len(objects) == 0:
            log.error( 'skipping plot titled {0} because there are no objects to plot...'.format( title ) )
            return

        if type == 'line':
            self._raw_plot_line( title, objects, days )
        elif type == 'stacked':
            self._raw_plot_stacked( title, objects, days )
        elif type == 'diffbar':
            self._raw_plot_diff( title, objects, days )
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

        ceilings = []
        floor = 0
        for key, balance in objects:
            ceiling = [  balance.interpolate(X[i]) for i in range(len(X)) ]
            ax.annotate( ' ' + key, xy=( maxTimestamp, floor + ceiling[-1] / 2.0 ) )
            ceilings.append(ceiling)
            floor = floor + ceiling[-1]

        ax.stackplot( summed.timestampsAsDateTime(), ceilings, baseline="zero" )


        ax.grid(True)
        if days is not None and len(objects):
            ax.set_xlim( [ maxTimestamp - datetime.timedelta(days=days) ], maxTimestamp )

        self._pdf.savefig( bbox_inches='tight', dpi=160 )

    def _raw_plot_diff(self, title, objects, days=7):
        days = int(days)

        fig, ax = plt.subplots()
        fig.set_figheight(12)   # inches..
        fig.set_figwidth(20)

        ax.set_title(title, fontsize=18)

        object = objects[0][1]

        # find the end of this plot
        maxTimestamp = object.maxTimestampAsDateTime()
        now = datetime.datetime.utcnow()
        now = now.replace(hour=23, minute=59, second=0, microsecond=0  )

        X = [ now - datetime.timedelta( days=i ) for i in range(days) ]
        X.reverse()
        assert isinstance(object, common.balanceData.BalanceData )
        Y = [ object.diff( x - datetime.timedelta(days=1) , x ) for x in X ]

        # offset X by 1 day to line the labels correctly..
        X = [ x - datetime.timedelta(days=1) for x in X ]
        barlist = ax.bar( X, Y, align='center', ecolor='k' )
        for k, v in enumerate(barlist):
            v.set_facecolor( 'g' if Y[k] >= 0 else 'r' )

        ax.grid(True)

        ax.xaxis.set_major_formatter( ticker.FuncFormatter( dates.DateFormatter( "%a %d" ) ) )

        self._pdf.savefig( bbox_inches='tight', dpi=160 )



