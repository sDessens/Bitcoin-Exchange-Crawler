# Module allows the retrieval of balances from Bitmex

import json
import urllib.request, urllib.error, urllib.parse
import time
import hashlib
import hmac
import logging

log = logging.getLogger( 'main.exchanges.bitmex' )


class BitmexLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = KrakenApi(self._pubkey, self._privkey)
        js = api.getBalance()
        return js['walletBalance'] * 0.00000001


class KrakenApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv

    def getBalance(self):
        url = 'https://www.bitmex.com'
        uri = '/api/v1/user/margin'

        nonce = int(time.time()) + 1000
        data = ''

        # print "Computing HMAC: %s" % verb + path + str(nonce) + data
        message = 'GET' + uri + str(nonce) + data

        signature = hmac.new(self.priv, message, digestmod=hashlib.sha256).hexdigest()

        headers = {
            'api-expires' : nonce,
            'api-key': self.pub,
            'api-signature': signature
        }

        ret = urllib.request.urlopen(urllib.request.Request(url + uri, headers=headers))
        return json.loads(ret.read())
