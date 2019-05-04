# Module allows query of balances from Bter

import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import time
import hashlib
import hmac
import logging
from common.conversiontable import ConversionException, ConversionTable

log = logging.getLogger('main.exchanges.bter')


class BterLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BterApi(self._pubkey, self._privkey)

        self.table = self._buildConversionTable(api)

        balance = api.query_private('getfunds', {})
        print(balance)
        total = 0.0

        if 'locked_funds' in balance:
            for k, v in list(balance['locked_funds'].items()):
                total += self._convert( k, 'BTC', float(v) )

        if 'available_funds' in balance:
            for k, v in list(balance['available_funds'].items()):
                total += self._convert( k, 'BTC', float(v) )

        return total

    def _buildConversionTable(self, api):
        tickers = api.query_public('tickers')

        markets = dict()

        for k, v in list(tickers.items()):
            buy = float(v['buy'])
            sell = float(v['sell'])
            avg = ( buy + sell ) / 2.0
            if avg == 0:
                log.warning( 'could not determine exchange rate of {}'.format(k) )
                continue
            diff = abs( buy - sell ) / avg

            primary, secondary = k.upper().split('_')
            markets[(primary, secondary)] = ( avg, 1.0 + diff )

        return ConversionTable( markets )

    def _convert(self, table, fromStock, toStock, amount):
        try:
            result = table.convert(fromStock.upper(), toStock.upper(), amount)
            return result
        except ConversionException as e:
            log.info(e)
            return 0


class BterApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def post(self, path, params, headers = {}):
        url = 'https://data.bter.com' + path
        post = urllib.parse.urlencode( params )
        headers['user-agent'] = 'Mozilla/5.0'
        ret = urllib.request.urlopen(urllib.request.Request( url, post, headers ))
        return json.loads(ret.read())

    def get(self, path, headers = {}):
        url = 'https://data.bter.com' + path
        headers['user-agent'] = 'Mozilla/5.0'
        req = urllib.request.urlopen( urllib.request.Request( url, headers=headers ) )
        return json.loads(req.read())

    def query_public(self, method, retry = 4 ):
        uri = '/api/1/' + method
        for _ in range(retry):
            try:
                return self.get( uri )
            except:
                pass
        raise


    def query_private(self, method, params, retry = 4):
        uri = '/api/1/private/' + method
        params['nonce'] = int(time.time()*1000)
        post = urllib.parse.urlencode( params )
        signature = hmac.new( self.priv, post, hashlib.sha512 )
        headers = dict(Sign=signature.hexdigest(), Key=self.pub)
        for _ in range(retry):
            try:
                data = self.post( uri, params, headers )
                if data['result'] == 'false':
                    raise Exception( 'Bter: ' + data['message'] )
                return data
            except:
                pass
        raise
