import requests  # pip install requests
import json
import base64
import hashlib
import hmac
import urllib2
import time #for nonce
import logging

from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.bitfinex' )

def getInstance():
    return BitfinexVisitor()

class BitfinexVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'bitfinex'
        except Exception as e:
            return False

    def visit( self, json ):
        api = BitfinexAPI( json['pubkey'], json['privkey'] )
        out = Collection()
        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        totals = []
        #fix for incorrect total value because of un synchronized orders and wallet call
        for i in range(3):
            total =0
            for k, v in wallet.items():
                total += table.convert(k, 'BTC', v)
            totals.append(total)
            time.sleep(0.01)

        out[json['out']] = PartialBalance(sorted(totals)[len(totals)/2])


        return out
class BitfinexAPI:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)
        self.url = 'https://api.bitfinex.com'


    def _getAuthenticated(self, uri, params):
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

    def _getMarkets(self):
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
        for pri, sec in self._getMarkets():
            uri = '/v1/pubticker/%s%s' % (pri, sec)
            js = self._get_public( uri)
            bid = float(js['bid'])
            ask = float(js['ask'])
            avg = (bid + ask) / 2
            diff = abs(bid - ask) / avg
            graph[(pri, sec)] = (avg, diff)
        return graph

