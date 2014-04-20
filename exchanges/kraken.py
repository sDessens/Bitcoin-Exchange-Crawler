#-------------------------------------------------------------------------------
# Name          kraken
# Purpose:      Module allows the retrieval of balances from Kraken
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import json
import urllib
import urllib2
import time
import hashlib
import hmac
import base64
import logging
from common.writeable.singleDatapoint import SingleDatapoint


log = logging.getLogger( 'main.exchanges.kraken' )

def getInstance():
    return KrakenVisitor()

class KrakenVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'kraken'
        except Exception as e:
            return False

    def visit( self, obj ):
        api = KrakenApi( obj['pubkey'], obj['privkey'] )
        b = SingleDatapoint()
        b.addBalance( obj['name'], api.getBalance( 'BTC' ) )
        return b

class KrakenApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv

    def getBalance(self, key):
        key = { 'BTC' : 'XBTC',
                'EUR' : 'ZEUR',
                'USD' : 'ZUSD'}[key.upper()]

        json = self._query_private( 'TradeBalance', { 'asset' : key } )
        return self._parseResponse( json )

    def _parseResponse(self, json):
        if 'result' in json:
            return float(json['result']['tb'])
        else:
            log.error( '{0}'.format( str( json['error']) ) )
            raise Exception()

    def _query(self, path, params, headers = {}):
        url = 'https://api.kraken.com' + path
        post = urllib.urlencode( params )
        headers['user-agent'] = 'bot'
        ret = urllib2.urlopen(urllib2.Request( url, post, headers ))
        print ret.read()
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