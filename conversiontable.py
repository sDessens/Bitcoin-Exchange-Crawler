
import Queue

class Graph:
    def __init__(self, markets):
        uniqueMarkets = set( a for a, b in markets ) | \
                        set( b for a, b in markets )

        connections = dict.fromkeys(uniqueMarkets, set() )
        conversionRates = {}
        costs = {}

        # primary, secondary, rate, cost
        for (a, b), (r, c) in markets.items():
            connections[a] = connections[a] | {b}
            connections[b] = connections[b] | {a}
            conversionRates[ (a, b) ] = r
            conversionRates[ (b, a) ] = 1.0/r
            costs[ (a, b) ] = c
            costs[ (b, a) ] = c

        self.connections = connections
        self.conversionRates = conversionRates
        self.costs = costs

    def computeExchangeRate(self, primary, secondary):
        # the state is a tuple of:
        # ( current cost,
        #   current stock,
        #   current conversion rate,
        #   set of all visited stocks )
        #
        initialState = ( 0, primary, 1, {primary} )
        queue = Queue.PriorityQueue()

        queue.put( initialState )

        while queue.not_empty:
            # grab next state
            (cost, stock, rate, visited) = queue.get()

            if stock == secondary:
                return rate

            for childStock in self.connections[ stock ]:
                arc = ( stock, childStock )
                childState = ( cost + self.costs[arc],
                               childStock,
                               rate * self.conversionRates[arc],
                               visited | {childStock} )
                #print childState
                queue.put( childState )

        raise Exception( 'could not convert {0} to {1}'.format(primary, secondary) )


class ConversionTable:
    ##Initialize an conversion table that allows converting
    # any stock in the table to any other stock
    #
    # @param markets an dictionary (primary, secondary) -> (rate, cost)
    # where rate is the exchange rate of primary in terms of secondary,
    # and cost is the cost of this path. An lower cost makes it more likely
    # that an conversion will go through this market
    def __init__(self, markets):
        uniqueMarkets = set( a for a, b in markets ) | \
                        set( b for a, b in markets )

        conversionRate = {}

        graph = Graph( markets )

        for primary in uniqueMarkets:
            for secondary in uniqueMarkets:
                rate = graph.computeExchangeRate( primary, secondary )
                print primary, '->', secondary, '=', rate
                conversionRate[(primary, secondary)] = rate

        self.conversionRate = conversionRate

    def convert(self, fromStock, toStock, amount ):
        total = self.conversionRate[(fromStock, toStock)] * amount
        print amount, fromStock, 'is', total, toStock
        return total

def main():
    d = {
        ('DGC', 'BTC') : (0.01, 2), # e.g. 0.01 DGC = 1 BTC
        ('LTC', 'BTC') : (0.02, 1),
        ('XPM', 'LTC') : (0.1, 1)
    }

    tab = ConversionTable( d )

    tab.convert( 'DGC', 'BTC', 100 )
    tab.convert( 'BTC', 'BTC', 100 )
    tab.convert( 'LTC', 'BTC', 10 )

if __name__ == '__main__':
    main()


