## this module acts as a implementation for all heavy-lifting plotting stuff

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import datetime
import math

import common.balanceData


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
        if type == 'stacked':
            return self._raw_plot_stacked( objects, days )
        if type == 'diffbar':
            return self._raw_plot_diffbar( objects, days )
        if type == 'histodiff':
            return self._raw_plot_histodiff( objects, days )
        if type == 'bar':
            return self._raw_plot_bar( objects, days )
        else:
            return None

    ## plot bog-standard line graph
    def _raw_plot_line(self, objects, days ):
        fig, ax = plt.subplots()

        # find the min/max of this plot
        maxTimestamp = max( [ balance.maxTimestampAsDateTime() for key, balance in objects ] )
        minTimestamp = min( [ balance.minTimestampAsDateTime() for key, balance in objects ] )
        if days is not None:
            if days > 0: minTimestamp = maxTimestamp - datetime.timedelta(days=days)
            if days < 0: maxTimestamp = minTimestamp - datetime.timedelta(days=days)

        for key, balance in objects:
            ax.plot( balance.timestampsAsDateTime(), balance.balance(), label=key )
            ax.annotate( ' ' + key, xy=( maxTimestamp, balance.interpolate( maxTimestamp ) ) )

        ax.grid(True)
        if days is not None and len(objects):
            ax.set_xlim( [minTimestamp], maxTimestamp )

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
        avg = sum(Y) / len(Y)

        # offset X by 1 day to line the labels correctly..
        X = [ x - datetime.timedelta(days=1) for x in X ]
        barlist = ax.bar( X, Y, align='center', ecolor='k' )
        for k, v in enumerate(barlist):
            v.set_facecolor( 'g' if Y[k] >= 0 else 'r' )

        ax.plot( [min(X), max(X)], [avg, avg], 'k', alpha=.5 )

        ax.grid(True)

        if days < 30:
            ax.xaxis.set_major_formatter( ticker.FuncFormatter( dates.DateFormatter( "%a %d" ) ) )

        return fig, ax

    ## plot bar chart based on the diff of the first input object.
    def _raw_plot_histodiff(self, objects, days):
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


        binWidth = 0.05
        targetBin = [ int(math.floor( y / binWidth )) for y in Y ]
        print targetBin
        binCount = max(targetBin) - min(targetBin) + 1
        minBin = min(targetBin)
        bins = [0] * binCount
        for bin in targetBin:
            bins[ bin - minBin ] += 1

        X = [ (i + minBin) * binWidth for i in range(len(bins)) ]

        barlist = plt.bar( X, bins, binWidth )
        for k, v in enumerate(barlist):
            if X[k] >= 0:
                v.set_facecolor( 'g' )
            else:
                v.set_facecolor( 'r' )

        print barlist
        ax.grid(True)

        return fig, ax

    def _raw_plot_bar(self, objects, days):
        fig, ax = plt.subplots()

        object = objects[0][1]

        if days is None:
            days = (datetime.datetime.utcnow() - object.minTimestampAsDateTime()).days + 1
        else:
            days = int(days)

        now = datetime.datetime.utcnow()
        now = now.replace(hour=23, minute=59, second=0, microsecond=0)

        X = [ now - datetime.timedelta( days=i ) for i in range(days) ]
        X.reverse()
        assert isinstance(object, common.balanceData.BalanceData )
        Y = [ object.interpolate(x) for x in X ]
        avg = sum(Y) / len(Y)

        # offset X by 1 day to line the labels correctly..
        X = [ x - datetime.timedelta(days=1) for x in X ]
        barlist = ax.bar( X, Y, align='center', ecolor='k' )
        for k, v in enumerate(barlist):
            v.set_facecolor( 'g' if Y[k] >= 0 else 'r' )

        ax.plot( [min(X), max(X)], [avg, avg], 'k', alpha=.5 )

        ax.grid(True)

        if days < 30:
            ax.xaxis.set_major_formatter( ticker.FuncFormatter( dates.DateFormatter( "%a %d" ) ) )

        return fig, ax
