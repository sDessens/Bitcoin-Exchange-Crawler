# Module implements an  process visitor that exports data
# to PDF format using the matplotlib library.


from common.resources.file import File
from common.resources.fullBalance import FullBalance
from common.matplotlibHelper import MatplotlibHelper
import common.balanceData
import common.tempFileLib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import logging
import traceback
log = logging.getLogger( 'main.process.matplotlibpdf' )


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
        self._helper = MatplotlibHelper()

    ## add a view to the existing pdf page
    #  @param json block of data that contains options.
    #  @param resources array of common.writable.*
    #  @return nothing, but mutates internal state
    def addView(self, json, resources):
        title = json['title'] if 'title' in json else ''
        type = json['plot'] if 'plot' in json else 'line'
        sources = json['source']
        days = json['days'] if 'days' in json else None
        width = json['width']/96.0 if 'width' in json else 20
        height = json['height']/96.0 if 'height' in json else 12

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

        ret = self._helper.plot( type, objects, days )
        if ret is None:
            log.error( 'unknown plot type {0}'.format(type) )
            return
        fig, ax = ret

        fig.set_figheight(height)
        fig.set_figwidth(width)
        if len(title):
            ax.set_title(title, fontsize=18)
        self._pdf.savefig( bbox_inches='tight', dpi=160 )

    ## save and close the plot.
    #  implementation must call this function, or a memory leak will occur.
    def finalize(self):
        self._pdf.close()
        plt.close()

