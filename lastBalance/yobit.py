# Module allows the retrieval of balances from BTC-e

import urllib
import urllib2                         
import json
import hmac
import time
import hashlib
from common.conversiontable import ConversionTable, ConversionException
import logging

log = logging.getLogger('main.read.btce')


class YobitApiException(Exception):
    pass


class YobitNoTradesApiException(YobitApiException):
    pass


class YobitInvalidApiKeyException(YobitApiException):
    pass

class YobitInvalidPairException(YobitApiException):
    pass


def throw_yobit_exception(response):
    if int(response['success']) == 1:
        return

    error_string = response['error']
    if error_string == 'no trades':
        raise YobitNoTradesApiException(error_string)
    elif error_string == 'invalid api key':
        raise YobitInvalidApiKeyException(error_string)
    else:
        raise YobitApiException(error_string)


class YobitLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = YobitApi(self._pubkey, self._privkey, "btc")
        return api.calculateAvailableFunds()

    def crawl_trades(self):
        pairs = ['btc_usd', 'eth_btc', 'eth_usd']
        api = YobitApi(self._pubkey, self._privkey, "btc")
        trades = {}
        for pair in pairs:
            start = 0
            size = 1000
            while True:
                try:
                    new_trades = api.getTrades(start, size, pair)
                except YobitNoTradesApiException:
                    break

                trades.update(new_trades)
                start += size
                time.sleep(1)  # do not spam
        return trades


class YobitApi:
    def __init__(self, APIKey, Secret, tovalue):
        self.APIKey = str(APIKey)
        self.Secret = str(Secret)
        self.toValue = tovalue
        self.nonce = int((time.time() * 1000 - (1481463210000)) / 100)
        self.url = 'https://yobit.net'

    def query_public(self, uri):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "python"
        }
        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_private(self, method, uri, req={}):
        req['method'] = method
        req['nonce'] = self.nonce
        post_data = urllib.urlencode(req)
        self.nonce += 1

        sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': self.APIKey,
            'user-agent': 'python'
        }

        request = urllib2.Request(self.url + uri, headers=headers, data=urllib.urlencode(req))
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        reply = json.loads(data)

        throw_yobit_exception(reply)
        if 'return' in reply:
            return reply['return']
        else:
            return {}

    def calculateAvailableFunds(self):
        wallet = self.query_private('getInfo', '/tapi')
        print wallet
        if wallet is None:
            return 0

        funds = wallet['funds_incl_orders']
        total = 0
        # calculate funds
        for key, amount in funds.iteritems():
            if key == 'btc':
                total += amount
            else:
                try:
                    ticker = self.getTicker(key + '_btc')
                    price = (ticker['sell'] + ticker['buy']) / 2
                    total += amount * price;
                except YobitInvalidPairException:
                    ticker = self.getTicker('btc_' + key)
                    price = (ticker['sell'] + ticker['buy']) / 2
                    total += amount / price

        return total

    def getTicker(self, pair):
        ret = self.query_public('/api/2/'+pair+'/ticker')
        if 'error' in ret and ret['error'] == "invalid pair":
            raise YobitInvalidPairException(pair)
        print pair, ret
        return ret['ticker']

    def getTrades(self, start, count, pair='eth_btc'):
        params = {
            "from": start,
            "count": count,
            "pair": pair
        }
        history = self.query_private('TradeHistory', '/tapi', params)
        if history:
            return history
        raise YobitNoTradesApiException