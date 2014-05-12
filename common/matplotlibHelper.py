## this module acts as a implementation for all heavy-lifting plotting stuff

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import datetime

import common.balanceData
from matplotlib.patches import Polygon



## this class defined various raw plotting functions.
#  the size and title should be set by the caller.
#  the plot should also be saved by the caller.
class MatplotlibHelper:
    def __init__(self):
        pass;

    ## plot 'type' graph
    #  returns fig, ax. Or None if no 'type' is not valid.
    #  @param type the type of the plot (str)
    #  @param objects array of (name, balanceData)
    #  @param days the amount of days to plot
    def plot(self, type, objects, days=None):
        assert( all( [ isinstance(x[1], common.balanceData.BalanceData) for x in objects ] ) )

        if type == 'line':
            return self._raw_plot_line( objects, days )
        elif type == 'stacked':
            return self._raw_plot_stacked( objects, days )
        elif type == 'diffbar':
            return self._raw_plot_diffbar( objects, days )
        elif type == 'stackedbar':
            return self._raw_plot_stackedbar( objects, days )
        else:
            return None

    ## plot bog-standard line graph
    def _raw_plot_line(self, objects, days ):
        fig, ax = plt.subplots()

        # find the end of this plot
        maxTimestamp = max( [ balance.maxTimestampAsDateTime() for key, balance in objects ] )

        for key, balance in objects:
            ax.plot( balance.timestampsAsDateTime(), balance.balance(), label=key )
            ax.annotate( ' ' + key, xy=( maxTimestamp, balance.interpolate( maxTimestamp ) ) )

        ax.grid(True)
        if days is not None and len(objects):
            ax.set_xlim( [ maxTimestamp - datetime.timedelta(days=days) ], maxTimestamp )

        return fig, ax

    ## plo stacked line chart
    def _raw_plot_stacked(self, objects, days):
        fig, ax = plt.subplots()

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

        return fig, ax

    ## plot bar chart based on the diff of the first input object.
    def _raw_plot_diffbar(self, objects, days):
        fig, ax = plt.subplots()

        object = objects[0][1]

        if days is None:
            days = (datetime.datetime.utcnow() - object.minTimestampAsDateTime()).days + 1
        else:
            days = int(days)

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

        if days < 30:
            ax.xaxis.set_major_formatter( ticker.FuncFormatter( dates.DateFormatter( "%a %d" ) ) )

        return fig, ax

    def _raw_plot_stackedbar(self, objects, days):
        import math
        import random

        fig, ax = plt.subplots()

        def genRect( x, y, w, h, color ):
            return Polygon( [(x, y), (x+w, y), (x+w, y+h), (x, y+h)], fc=color )

        def genPatch( x1, y1, h1, x2, y2, h2, color ):
            return Polygon( [(x1, y1), (x2, y2), (x2, y2+h2), (x1, y1+h1)], alpha=0.1, fc=color, edgecolor='black', lw=1)


        now = datetime.datetime.utcnow()
        now = now.replace(hour=23, minute=59, second=0, microsecond=0  )

        X = [ now - datetime.timedelta( days=i ) for i in range(days) ]
        X.reverse()

        raw = [
            [ objects[i][1].interpolate( x ) for i in range(len(objects))  ]
            for x in X
        ]

        """
        current = [0.5] * 13

        raw = []

        for i in range(7):
            raw.append( current )
            current = [ max(0.1,  c + random.random() - 0.4) for c in current ]

        raw = [[2.058,	2.008,	1.758,	1.122,	0.742,	0.601,	2.001,	0.743,	1.484,	2.944,	6,	0.903,	0.447],
        [2.058,	1.944,	1.77,	1.122,	0.742,	0.598,	2.001,	0.771,	1.503,	2.75,	6,	0.981,	0.46],
        [2.058,	1.954,	1.836,	1.122,	0.737,	0.604,	2.001,	0.797,	1.563,	2.751,	6,	0.99,	0.472],
        [2.116,	1.938,	1.838,	1.122,	0.747,	0.611,	2.001,	0.796,	1.606,	2.727,	6,	0.997,	0.46],
        [2.146,	2.008,	1.899,	1.122,	0.756,	0.607,	2.001,	0.795,	1.663,	2.882,	6,	1.003,	0.461],
        [2.167,	2.102,	1.942,	1.122,	0.755,	0.642,	2.001,	0.801,	1.692,	2.924,	6,	1.005,	0.462],
        [2.141,	2.137,	1.967,	1.122,	0.75,	0.646,	2.001,	0.79,	1.694,	2.93,	6,	0.999,	0.466]]
        """

        colors = [ plt.get_cmap('Set1')( x/float(len(raw[0])) ) for x in range(len(raw[0])) ]
        #colors = [ ax._get_lines.color_cycle.next() for _ in range(len(raw[0])) ]
        #colors = [ 'red', 'blue', 'green', 'cyan', 'yellow' ]

        w = 0.4
        x = 1.0 - w/2


        for day in raw:
            colorIndex = 0
            totalHeight = 0
            for height in day:
                color = colors[colorIndex]
                poly = genRect( x, totalHeight, w, height, color )
                plt.gca().add_patch(poly)
                plt.annotate( '{0:.3f}'.format(height), xy=(x + w/2, totalHeight + height / 2), ha='center',
                              va='center' )
                totalHeight += height
                colorIndex += 1
            x += 1



        x = 1.0 + w/2
        w = 1 - w


        for old, new in zip( raw, raw[1:] ):
            colorIndex = 0
            totalLeft = 0
            totalRight = 0
            for left, right in zip( old, new ):
                color = colors[colorIndex]
                poly = genPatch( x, totalLeft, left, x+w, totalRight, right, color )
                plt.gca().add_patch(poly)
                #string = '{0:.1f}%'.format( (right-left) / left * 100.0 ) # percentage
                string = '{0:.0f} mBTC'.format( (right - left) * 1000 )
                l = (totalLeft + left/2)
                r = (totalRight + right/2)
                slope = (totalLeft - totalRight) / w/2
                angle = math.sin(-slope) / math.pi * 180
                angle = 0

                plt.annotate( string , xy=( x + w/2, totalLeft/2 + left/4 + totalRight/2 + right/4 ),
                              ha='center', va='center', rotation=angle )
                totalLeft += left
                totalRight += right
                colorIndex += 1
            x += 1
            print '----------'


        ax.set_xlim( 0, 8 )
        ax.set_ylim( 0, sum(raw[-1])*1.2 )

        return fig, ax