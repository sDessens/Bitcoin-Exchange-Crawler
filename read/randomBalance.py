# this module can be used to Generate random-walk based FullBalance resource.


from common.resources.collection import Collection
from common.resources.fullBalance import FullBalance
from common.balanceData import BalanceData

import random
import time

def getInstance():
    return randomReadVisitor()

## this is a stub db reader. It provides an template that provides all
#  required functionality for an db reader
class randomReadVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object.
    #  @return true if object is accepted
    #  May not throw exceptions.
    def accept( self, json ):
        try:
            return json['type'] == 'random'
        except Exception as e:
            return False

    ## parse and return data specified in json.
    #  @return common.writable.collection
    #  may throw an exception
    def visit( self, json ):
        out = Collection()

        days = json['days'] if 'days' in json else 7

        rd = random.Random()

        for name in json['data']:
            x = range( int(time.time() - 60 * 60 * 24 * days), int(time.time()), 60*30 )
            y = []
            current = 1
            for timestamp in x:
                y.append(current)
                current = max(0, current + 0.2 * (rd.random() - 0.5) )

            out[name] = FullBalance( BalanceData( x, y ) )

        return out