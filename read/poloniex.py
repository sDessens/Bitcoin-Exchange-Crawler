# Module allows the retrieval of balances from Cex.io

import json
import urllib2
import urllib
import time
import hashlib
import hmac
import logging
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.poloniex' )

def getInstance():
    return PoloniexApiVisitor()

class PoloniexApiVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'poloniex'
        except Exception as e:
            return False

    def visit( self, json ):
        api = PoloniexApi( json['pubkey'], json['privkey'] )
        out = Collection()
        markets = api.getMarketsGraph()
        wallet = api.getWallet(markets)
        table = ConversionTable(markets)
        total = 0
        for k, v in wallet.items():
            total += table.convert(k, 'BTC', v)
        out[json['out']] = PartialBalance( total )
        return out

class PoloniexApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def _get(self, command, params):
        www = "https://poloniex.com/tradingApi"
        params['nonce'] = str(int(time.time()*1000))
        params['command'] = command
        sign= hmac.new(self.priv, urllib.urlencode(params), hashlib.sha512).hexdigest()

        req = urllib2.Request(www, urllib.urlencode(params))

        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        req.add_header("Sign", sign)
        req.add_header("Key", self.pub)
        return json.loads(urllib2.urlopen(req).read())

    def _get_public(self, command):
        req = urllib2.Request("https://poloniex.com/public?command=" + command)
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib2.urlopen(req).read())

    def getWallet(self, markets):
        command = 'returnCompleteBalances'

        js = self._get(command, {})

        wallet = {}
        for k, v in js.items():
            if len(k) == 3 or len(k) == 4:
                # Some markets are inactive so we need to check if the stock exists in markets
                for market in markets:
                    if market[0] == k or market[1] == k:
                        wallet[k] = float(v["available"])
                        wallet[k] += float(v["onOrders"])

        return wallet

    def getMarketsGraph(self):
        graph = {}
        js = self._get_public('returnTicker')
        for key, value in js.iteritems():
            keys = key.split("_")
            pair = (keys[1], keys[0])
            if "_" in key:
                rate = (float(value['lowestAsk']) + float(value['highestBid'])) / 2.0
                cost = (float(value['lowestAsk']) - rate) / rate
                graph[pair] = (rate, cost)

        return graph

def main():
    vis = PoloniexApiVisitor()
    json = { 'type':'poloniex',
             'out':'poloniex-test',
             'pubkey':'',
             'privkey':''}

    assert( vis.accept( json ) )

    print vis.visit( json )

if __name__ == '__main__':
    main()
