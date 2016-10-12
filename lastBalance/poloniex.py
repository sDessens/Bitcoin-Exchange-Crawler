# Module allows the retrieval of balances from Poloniex

import json
import urllib2
import urllib
import time
import hashlib
import hmac
import logging
from common.conversiontable import ConversionTable

log = logging.getLogger('main.exchanges.poloniex')


class PoloniexLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = PoloniexApi(self._pubkey, self._privkey)

        markets = api.getMarketsGraph()
        wallet = api.getWallet()
        open_orders = api.getOpenoOrders()
        table = ConversionTable(markets)
        funds = {}
        total = 0

        # Although the getWallet call returns the amount of funds in orders and the total
        # value in btc, the api ia bugged and returns less funds than there actually are
        # when there are multiple orders for the exact same amount at different markets.
        # We are forced to parse the in orders ourselves to get ocrrect results
        for pair, details in wallet.items():
            amount = float(details['available'])
            if amount:
                funds[pair] = float(details['available'])

        for pair, orders in open_orders.items():
            if orders:
                for order in orders:
                    if order['type'] == 'buy':
                        funds[pair.partition('_')[0]] += float(order['total'])
                    else:
                        funds[pair.partition('_')[2]] += float(order['amount'])

        for k, v in funds.items():
            if v:
                total += table.convert(k, 'BTC', v)
        return total


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

    def getOpenoOrders(self):
        command = 'returnOpenOrders'
        return self._get(command, {'currencyPair': 'all'})

    def getWallet(self):
        command = 'returnCompleteBalances'
        return self._get(command, {})

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
