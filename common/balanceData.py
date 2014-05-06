# Simple class to hold the (X, Y) data from a single source.


from bisect import bisect_left
import datetime
import time

class BalanceData:
    ##Construct an instance of the BalanceData class
    # @param timestamps a list of integer values representing unix timestamp
    # @param values a list of float values representing the value
    def __init__( self, timestamps = None, values = None ):
        self._timestamps = timestamps if timestamps is not None else []
        self._balance = values if values is not None else []

        # assert if the list is non sorted
        assert( all(b > a for a, b in zip(self._timestamps, self._timestamps[1:])) )

    ##returns a new BalanceData object
    #
    def generateDiff( self, days = 1 ):
        seconds = days * 24 * 60 * 60
        new = BalanceData()
        # start at the last timestamp
        timestamp = self._timestamps[-1]
        while timestamp > self._timestamps[0]:
            diff = self.diff( timestamp - seconds, timestamp ) / days
            new._timestamps.append( timestamp )
            new._balance.append( diff )
            timestamp -= 3600

        new._timestamps.reverse()
        new._balance.reverse()

        return new

    ##calculate the difference Y between given points
    # @param begin begin of sample
    # @param end end of sample
    def diff( self, begin, end ):
        return self.interpolate( end ) - self.interpolate( begin )

    ##Query the value at a certain point in time
    # @param timestamp integer or float Unix timestamp or DateTime object
    # @return the interpolated Y value
    def interpolate( self, timestamp ):
        if type(timestamp) is datetime.datetime:
            timestamp = float(time.mktime( timestamp.timetuple() ))

        if timestamp < self._timestamps[0]:
            return 0
        if timestamp > self._timestamps[-1]:
            return self._balance[-1]

        index = bisect_left(self._timestamps,timestamp,0,len( self._timestamps ))

        if timestamp == self._timestamps[index]:
            # perfect match
            return self._balance[index]
        else:
            #interpolation required
            a = self._balance[index-1]
            b = self._balance[index]
            ab = self._timestamps[ index ] - self._timestamps[ index - 1 ]
            distance = timestamp - self._timestamps[ index - 1 ]
            progress = distance / ab
            assert( progress >= 0 )
            assert( progress < 1 )
            return b * progress + a * ( 1.0 - progress )

    def timestampAsUnix(self):
        return self._timestamps

    def timestampsAsDateTime(self):
        return [ datetime.datetime.fromtimestamp( x ) for x in self._timestamps ]

    def maxTimestampAsDateTime(self):
        return datetime.datetime.fromtimestamp( self._timestamps[-1] )

    def minTimestampAsDateTime(self):
        return datetime.datetime.fromtimestamp( self._timestamps[0] )

    def balance(self):
        return self._balance

    def __len__(self):
        return len( self._balance )


##sum multiple BalanceData objects together
# @param array of BalanceData object
# @return the summed BalanceData object
def sum(data):
    timestampSet = set()
    for bd in data:
        timestampSet = timestampSet.union( bd._timestamps )

    timestamps = list( timestampSet )
    timestamps.sort()
    y = []
    for x in timestamps:
        val = 0
        for bd in data:
            val = val + bd.interpolate(x)
        y.append( val )

    return BalanceData( timestamps, y )