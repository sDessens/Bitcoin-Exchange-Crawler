import json
import base64
import hashlib
import hmac
import urllib2
import time
import logging

from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.bitfinex' )

import urllib
import httplib

class BitfinexLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BitfinexAPI(self._pubkey, self._privkey)

        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        totals = []
        #fix for incorrect total value because of un synchronized orders and wallet call
        for i in range(3):
            total = 0
            for k, v in wallet.items():
                total += table.convert(k, 'BTC', v)
            totals.append(total)
            time.sleep(0.01)

        return sorted(totals)[len(totals)/2]

    def crawl_trades(self):
        api = BitfinexAPI(self._pubkey, self._privkey)

        trades = {}

        for market in api.getMarkets():
            pair = ''.join(market)
            trades[pair] = []
            since = 0
            while True:
                js = api.getMyTrades(pair, since)
                trades[pair] += js
                if len(js) != api.MAX_MY_TRADES:
                    break
                since = int(float(max([str(x['timestamp']) for x in js])) + 1)

        return trades


class BitfinexAPI:
    MAX_MY_TRADES = 1000

    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)
        self.url = 'https://api.bitfinex.com'


    def _getAuthenticated(self, uri, params):
        h = urllib2.HTTPHandler(debuglevel=1)
        opener = urllib2.build_opener(h)
        urllib2.install_opener(opener)

        payloadObject = {
            'request': uri,
            'nonce': str(time.time()),
        }
        payloadObject.update(params)
        payload_json = json.dumps(payloadObject)

        payload = str(base64.b64encode(payload_json))

        m = hmac.new(self.priv,payload,hashlib.sha384).digest().encode('hex')

        # headers
        headers = {
                   'X-BFX-APIKEY' : self.pub,
                   'X-BFX-PAYLOAD' : base64.b64encode(payload_json),
                   'X-BFX-SIGNATURE' : m
                   }
        request = urllib2.Request(self.url+uri, data={}, headers=headers)
        try:
            ret = urllib2.urlopen(request)
            return json.loads(ret.read())
        except Exception as e:
            log.error( 'network error: ' + str(e) )
            print e.read()
            raise e

    def _get_public(self, uri):
        req = urllib2.Request(self.url + uri)
        return json.loads(urllib2.urlopen(req).read())

    def getWallet(self):
        uri = '/v1/balances'
        params = {
               'request':uri,
               'nonce': str(time.time()),
        }
        js = self._getAuthenticated(uri,params)
        wallet = {}
        if js != None:
            for balance in js:
                if balance['type'] == 'exchange':
                    k = balance['currency'].upper()
                    v = float(balance['amount'])
                    #since bitfinex has multiple wallets for the same currency we need to add all together
                    if k in wallet:
                        wallet[k] += v
                    else:
                        wallet[k] = v
        else:
            wallet = None
        return wallet

    def getMyTrades(self, pair, since):
        uri = '/v1/mytrades'
        params = {
            'request': uri,
            'nonce': str(time.time()),
            'symbol': pair,
            'timestamp': str(since),
            'limit_trades': self.MAX_MY_TRADES,
            'reverse': 1
        }
        js = self._getAuthenticated(uri, params)
        return js

    def getMarkets(self):
        uri = '/v1/symbols'
        markets = self._get_public( uri)
        splitsymbols = []

        for market in markets:
            pri = market[:3].upper()
            sec = market[-3:].upper()
            pair = (pri,sec)
            splitsymbols.append(pair)
        return splitsymbols

    def getMarketsGraph(self):
        graph = {}
        for pri, sec in self.getMarkets():
            uri = '/v1/pubticker/%s%s' % (pri, sec)
            js = self._get_public( uri)
            bid = float(js['bid'])
            ask = float(js['ask'])
            avg = (bid + ask) / 2
            diff = abs(bid - ask) / avg
            graph[(pri, sec)] = (avg, diff)
        return graph
