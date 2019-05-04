# Module allows conversion of an stock to a different stock. For
# example, one can query the amount of BTC 100000 DOGE is worth.
# The conversion rate from DOGE to BTC is then calculated using
# an search algorithm.

from queue import PriorityQueue
import logging

log = logging.getLogger('conversion_table')

class ConversionException(Exception):
    pass


class ConversionTable:
    ##Initialize an conversion table that allows converting
    # any stock in the table to any other stock
    #
    # @param markets an dictionary (primary, secondary) -> (rate, cost)
    # where rate is the exchange rate of primary in terms of secondary,
    # and cost is the cost of this path. An lower cost makes it more likely
    # that an conversion will go through this market. If you don't know, just
    # use 1 for the cost at every market. Cost must NOT be zero.
    def __init__(self, markets):
        uniqueMarkets = set(a for a, b in markets) | \
                        set(b for a, b in markets)

        connections = dict.fromkeys(uniqueMarkets, set())
        conversionRates = {}
        costs = {}

        # primary, secondary, rate, cost
        for (a, b), (r, c) in list(markets.items()):
            connections[a] = connections[a] | {b}
            connections[b] = connections[b] | {a}
            conversionRates[ (a, b) ] = r
            conversionRates[ (b, a) ] = 1.0/r
            costs[(a, b)] = c
            costs[(b, a)] = c

        self.connections = connections
        self.conversionRates = conversionRates
        self.costs = costs

    ##convert any stock to an different stock
    # @param fromStock the stock to convert from
    # @param toStock the stock to convert to
    # @param amount the amount to convert
    # @return the converted amount
    # can throw an ConversionException if conversion fails for some reason.
    def convert(self, fromStock, toStock, amount ):
        rate = self._computeExchangeRate(fromStock, toStock)
        total = rate * amount
        return total

    def try_convert(self, fromStock, toStock, amount):
        """ Identical to convert(), but returns 0.0 on failure """
        try:
            return self.convert(fromStock, toStock, amount)
        except ConversionException:
            log.warn('unable to convert {} to {}'.format(fromStock, toStock))
            return 0.0

    def _computeExchangeRate(self, primary, secondary):
        # this does a A* search with H = 0
        #
        # the state is a tuple of:
        # ( current cost,
        #   current stock,
        #   current conversion rate,
        #   set of all visited stocks )
        initialState = (0, primary, 1, {primary})
        queue = PriorityQueue()
        queue.put( initialState )

        if primary in self.connections:
            if len(self.connections[primary]) == 0:
                raise ConversionException( 'could not convert {0} to {1} because destination is unreachable'
                                           .format(primary, secondary) )

        while queue.qsize() > 0:
            (cost, stock, rate, visited) = queue.get()

            if stock == secondary:
                return rate

            if stock in self.connections:
                for childStock in self.connections[stock]:
                    if childStock not in visited:
                        arc = (stock, childStock)
                        childState = (cost + self.costs[arc],
                                      childStock,
                                      rate * self.conversionRates[arc],
                                      visited | {childStock})
                        queue.put(childState)

        raise ConversionException( 'could not convert {0} to {1} because destination is unreachable'
                                   .format(primary, secondary) )


