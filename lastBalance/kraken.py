# Module allows the retrieval of balances from Kraken

import json
import urllib
import urllib2
import time
import hashlib
import hmac
import base64
import logging

log = logging.getLogger( 'main.exchanges.kraken' )


class KrakenLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = KrakenApi(self._pubkey, self._privkey)
        return api.getBalance('BTC')

    def crawl_trades(self):
        api = KrakenApi(self._pubkey, self._privkey)
        js = api.getTradeHistory()
        return js['trades']

class KrakenApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv

    def getBalance(self, key):
        key = { 'BTC' : 'XXBT',
                'EUR' : 'ZEUR',
                'USD' : 'ZUSD'}[key.upper()]

        json = self._query_private( 'TradeBalance', { 'asset' : key } )
        return self._parseResponse(json)

    def getTradeHistory(self):
        json = self._query_private('TradesHistory', {})
        return json['result']

    def _parseResponse(self, json):
        if 'result' in json:
            print json
            return float(json['result']['eb'])
        else:
            log.error( '{0}'.format( str( json['error']) ) )
            raise Exception()

    def _query(self, path, params, headers = {}):
        url = 'https://api.kraken.com' + path
        post = urllib.urlencode( params )
        headers['user-agent'] = 'bot'
        ret = urllib2.urlopen(urllib2.Request( url, post, headers ))
        return json.loads(ret.read())

    def _query_public(self, method, params):
        return self._query( '/0/public/' + method, params )

    def _query_private(self, method, params):
        url = 'https://api.kraken.com/'
        path = '/0/private/' + method

        params['nonce'] = int(time.time()*1000)
        post = urllib.urlencode( params )
        message = path + hashlib.sha256(str(params['nonce']) + post).digest()
        signature = hmac.new(base64.b64decode(self.priv), message, hashlib.sha512)
        headers = {
            'API-Key': self.pub,
            'API-Sign': base64.b64encode(signature.digest())
        }

        return self._query( path, params, headers )