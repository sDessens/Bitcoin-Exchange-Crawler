# Module allows the retrieval of balances from Mintpal

import json
import urllib2
import time
import hashlib
import hmac
import logging
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.hitbtc' )

def getInstance():
    return MintpalVisitor()

class MintpalVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'hitbtc'
        except Exception as e:
            return False

    def visit( self, json ):
        api = MintpalApi( json['pubkey'], json['privkey'] )
        out = Collection()

        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in wallet.items():
            total += table.convert(k, 'BTC', v)
        out[json['out']] = PartialBalance( total )
        return out

class MintpalApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def _get(self, www, uri):
        uri += '?nonce={}'.format(str(int(time.time()*1000000)))
        uri += '&apikey={}'.format(self.pub)

        sign = hmac.new(self.priv, uri, hashlib.sha512).digest().encode('hex')

        req = urllib2.Request(www + uri)
        req.add_header('X-Signature', sign)
        return json.loads(urllib2.urlopen(req).read())

    def _get_public(self, www, uri):
        req = urllib2.Request(www + uri)
        return json.loads(urllib2.urlopen(req).read())

    def getWallet(self):
        www = 'https://api.hitbtc.com'
        out = {}

        for line in self._get(www, '/api/1/trading/balance')['balance']:
            out[line['currency_code']] = float(line['cash']) + float(line['reserved'])

        for line in self._get(www, '/api/1/payment/balance')['balance']:
            out[line['currency_code']] += float(line['balance'])

        return dict((k, v) for k, v in out.items() if v)

    def getMarketsGraph(self):
        www = 'https://api.hitbtc.com'

        symbols = []

        for line in self._get_public(www, '/api/1/public/symbols')['symbols']:
            symbol = line['symbol']
            if symbol.startswith('BTC'):
                symbols += [('BTC', symbol[3:])]
            if symbol.endswith('BTC'):
                symbols += [(symbol[:-3], 'BTC')]
            else:
                symbols += [(symbol[:-3], symbol[-3:])]

        graph = {}
        for pri, sec in symbols:
            js = self._get_public(www, '/api/1/public/{}/ticker'.format(pri+sec))
            bid = float(js['bid'])
            ask = float(js['ask'])
            avg = (bid + ask) / 2
            diff = abs(bid - ask) / avg
            graph[(pri, sec)] = (avg, diff)

        return graph