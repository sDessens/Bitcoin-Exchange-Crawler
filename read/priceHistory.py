import urllib2
import time
from calendar import timegm

from common.resources.fullBalance import FullBalance
from common.resources.collection import Collection
from common.balanceData import BalanceData


def getInstance():
    return PriceHistoryReadVisitor()


class PriceHistoryReadVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object.
    #  @return true if object is accepted
    #  May not throw exceptions.
    def accept( self, json ):
        try:
            return json['type'] == 'pricehistory'
        except Exception as e:
            return False

    ## parse and return data specified in json.
    #  @return common.writable.collection
    #  may throw an exception
    def visit( self, json ):

        arr = []
        csv = urllib2.urlopen('https://api.bitcoinaverage.com/history/USD/per_day_all_time_history.csv').read()
        for line in csv.split('\n')[1:-1]:
            parts = line.split(',')
            a = parts[0].partition(' ')[0] + ' UTC' # skip time, useless since it is always 00:00:00, append Timezone
            stamp = timegm(time.strptime(a, '%Y-%m-%d %Z'))
            price = parts[3]
            arr.append((int(stamp), float(price)))

        final_price = urllib2.urlopen('https://api.bitcoinaverage.com/ticker/global/USD/last').read()
        arr.append((time.time(), int(float(final_price))))

        out = Collection()
        out[json['out']] = FullBalance(BalanceData(
            [x[0] for x in arr],
            [x[1] for x in arr]))

        return out
