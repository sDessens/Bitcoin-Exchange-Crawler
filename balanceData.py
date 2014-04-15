from bisect import bisect_left
import datetime
import time

"""
Construct an instance of the BalanceData class

@param timestamps a list of integer values representing unix timestamp
@param values a list of float values representing the value

"""
class BalanceData:
    def __init__( self, timestamps = None, values =None ):
        self._timestamps = []
        self._balance = []
        if timestamps == None and values == None:
            return;

        self._timestamps = timestamps
        self._balance = values
        # assert if the list is non sorted
        assert( all(b >= a for a, b in zip(self._timestamps, self._timestamps[1:])) )
        
    """ @param data An array of BalanceData objects. In this case, the constructed object
      is consists of interpolated data from the argument.
      """        
    def sum(self, data):
        # argument is array of BalanceData
        # enumerate all timestamps
        timestampSet = set()
        for x in data:
            timestampSet = timestampSet.union( x._timestamps );
        self._timestamps = list( timestampSet )
        self._timestamps.sort()
        self._balance = [0] * len( self._timestamps );
        # for every balance data
        for balance in data:
            # for every timestamp
            for i in range( len(self._timestamps) ):
                stamp = self._timestamps[i];
                val = balance.interpolate( stamp )
                self._balance[i] += val;

    """
    returns a NEW chart
    """
    def generateDiff( self, days = 1 ):
        seconds = days * 24 * 60 * 60
        new = BalanceData()
        # start at the last timestamp
        timestamp = self._timestamps[-1]
        while timestamp > self._timestamps[0]:
            diff = self.diff( timestamp - seconds, timestamp ) / days
            new._timestamps.append( timestamp )
            new._balance.append( diff );
            timestamp -= 3600

        new._timestamps.reverse()
        new._balance.reverse()

        return new

    """
    returns the delta from 'timestamp' to 'timestamp + seconds'
    """
    def diff( self, begin, end ):
        return self.interpolate( end ) - self.interpolate( begin )

    def interpolate( self, timestamp ):
        if type(timestamp) is datetime.datetime:
            timestamp = float(time.mktime( timestamp.timetuple() ))

        if timestamp < self._timestamps[0]:
            return 0;
        if timestamp > self._timestamps[-1]:
            return self._balance[-1];

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
            assert( progress > 0 )
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
