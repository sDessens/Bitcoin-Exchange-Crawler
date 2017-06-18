# Module allows the retrieval of balances from BTC-e

import urllib
import urllib2
import base64
import json
import hmac
import time
import hashlib
from common.conversiontable import ConversionTable, ConversionException
import logging

log = logging.getLogger('main.read.bl3p')


class Bl3pApiException(Exception):
    pass


class Bl3pNoTradesApiException(Bl3pApiException):
    pass


class Bl3pInvalidApiKeyException(Bl3pApiException):
    pass

class Bl3pInvalidPairException(Bl3pApiException):
    pass

class Bl3pException(Bl3pApiException):
    pass

def throw_Bl3p_exception(response):
    if response['result'] == 'success':
        return

    error_string = response['data']['code']
    error_message = response['data']['message']
    if error_string == 'no trades':
        raise Bl3pNoTradesApiException(error_message)
    elif error_string == 'NOT_AUTHENTICATED':
        raise Bl3pInvalidApiKeyException(error_message)
    else:
        raise Bl3pApiException(error_message)


class Bl3pLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = Bl3pApi(self._pubkey, self._privkey, "btc")
        return api.calculateAvailableFunds()

    def crawl_trades(self):
        pairs = ['BTCEUR']
        api = Bl3pApi(self._pubkey, self._privkey, "btc")
        trades = {}
        for pair in pairs:
            start = 1
            size = 1000
            max_page = 0
            while start <= max_page or max_page == 0:
                try:
                    new_trades = api.getTrades(start, size, pair)
                    max_page =  new_trades['max_page']
                except Bl3pNoTradesApiException:
                    break
                for trade in new_trades['orders']:
                    trades.update(trade)
                start += 1
                time.sleep(1)  # do not spam
        return trades


class Bl3pApi:
    def __init__(self, APIKey, Secret, tovalue):
        self.APIKey = str(APIKey)
        self.Secret = base64.b64decode(Secret)
        self.toValue = tovalue
        self.nonce = int((time.time() * 1000 - (1481463210000)) / 100)
        self.url = 'https://api.bl3p.eu/1/'

    def query_public(self, uri):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "python"
        }
        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_private(self,  uri, req={}):
        post_data = urllib.urlencode(req)
        body = '%s%c%s' % (uri, 0x00, post_data)

        sign = hmac.new(self.Secret, body, hashlib.sha512).digest()
        headers = {
            'Rest-Sign': base64.b64encode(sign),
            'Rest-Key': self.APIKey,
            'user-agent': 'python'
        }

        request = urllib2.Request(self.url + uri, headers=headers, data=post_data)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        reply = json.loads(data)

        throw_Bl3p_exception(reply)
        if 'data' in reply:
            return reply['data']
        else:
            return {}

    def calculateAvailableFunds(self):
        wallet = self.query_private('GENMKT/money/info')
        print wallet
        if wallet is None:
            return 0

        funds = wallet['wallets']
        total = 0
        # calculate funds
        for key, obj in funds.iteritems():
            amount = float(obj['balance']['value'])
            if key == 'BTC':
                total += amount
            else:
                ticker = self.getTicker('BTC' + key)
                price = (float(ticker['ask']) + float(ticker['bid'])) / 2
                total += amount / price


        return total

    def getTicker(self, pair):
        ret = self.query_public(pair+'/ticker')
        if 'result' in ret and ret['result'] == "error":
            raise Bl3pException(pair)
        return ret

    def getTrades(self, start, count, pair='BTCEUR'):
        params = {
            "page": start,
            "recs_per_page":count
        }
        history = self.query_private(pair +'/money/orders/history', params)
        if history:
            return history
        raise Bl3pNoTradesApiException