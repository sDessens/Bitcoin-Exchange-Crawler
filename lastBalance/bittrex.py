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

log = logging.getLogger('main.read.bittrex')


class BittrexApiException(Exception):
    pass


class BittrexNoTradesApiException(BittrexApiException):
    pass


class BittrexInvalidApiKeyException(BittrexApiException):
    pass

class BittrexInvalidPairException(BittrexApiException):
    pass

class BittrexException(BittrexApiException):
    pass



class BittrexLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BittrexApi(self._pubkey, self._privkey, "btc")
        return api.calculateAvailableFunds()

    def crawl_trades(self):
        api = BittrexApi(self._pubkey, self._privkey, "btc")
        trades = {}
        start = 1
        size = 1000

        new_trades = api.getTrades(start, size)

        return new_trades

    def crawl_balance(self):
        api = BittrexApi(self._pubkey, self._privkey, "btc")
        total_btc = api.calculateAvailableFunds()
        wallet = api.getWallet()
        balances = {}
        for obj in wallet:
            amount = float(obj['Available'])
            if amount != 0:
                balances[obj['Currency']] = amount
        balances["Total_BTC"] = total_btc
        return balances

class BittrexApi:
    def __init__(self, APIKey, Secret, tovalue):
        self.APIKey = APIKey
        self.Secret = Secret
        self.toValue = tovalue
        self.url = 'https://bittrex.com/api/v1.1/'
        self.marketSummary = self.getTicker()

    def query_public(self, uri):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "python"
        }
        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        reply = json.loads(data)
        if reply['success'] == True:
            return reply['result']
        else:
            raise BittrexException(reply["message"])

    def query_private(self,  uri, req={}):
        req['nonce'] = int((time.time() * 1000 ))
        encoded_url = self.url + uri + '?apikey=' +self.APIKey + "&" + urllib.urlencode(req)

        sign = hmac.new(self.Secret, encoded_url, hashlib.sha512).hexdigest()
        headers = {
            'apisign': sign,
        }

        request = urllib2.Request(encoded_url, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        reply = json.loads(data)

        if reply['success'] == True:
            return reply['result']
        else:
            raise BittrexException(reply["message"])


    def getWallet(self):
        wallet = self.query_private('account/getbalances')
        print wallet
        if wallet is None:
            return 0

        return wallet

    def calculateAvailableFunds(self):
        funds = self.getWallet()
        if funds == 0:
            return 0
        total = 0
        # calculate funds
        for obj in funds:
            amount = float(obj['Balance'])
            if obj['Currency'] == 'BTC':
                total += amount
            else:
                if obj['Currency'] == 'USDT':
                    price = self.marketSummary[obj['Currency'] + "-" + 'BTC']
                    total += amount / price
                else:
                    price = self.marketSummary[ 'BTC' + "-" + obj['Currency']]
                    total += price * amount

        return total

    def getTicker(self):
        ret =  self.query_public('public/getmarketsummaries')
        marketPrice = {}
        for obj in ret:
            marketPrice[obj['MarketName']] = float(obj['Last'])
        return marketPrice

    def getTrades(self, start, count):
        params = {
            "page": start,
            "recs_per_page":count
        }
        history = self.query_private('account/getorderhistory')
        if history:
            return history
        raise BittrexNoTradesApiException
