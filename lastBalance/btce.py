# Module allows the retrieval of balances from BTC-e

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse                         
import json
import hmac
import time
import hashlib
from common.conversiontable import ConversionTable, ConversionException
import logging

log = logging.getLogger('main.read.btce')


class BtceApiException(Exception):
    pass


class BtceNoTradesApiException(BtceApiException):
    pass


class BtceInvalidApiKeyException(BtceApiException):
    pass


class BtceNoOrdersApiException(BtceApiException):
    pass

def throw_btce_exception(response):
    if int(response['success']) == 1:
        return

    error_string = response['error']
    if error_string == 'no trades':
        raise BtceNoTradesApiException(error_string)
    if error_string == 'no orders':
        raise BtceNoOrdersApiException(error_string)
    elif error_string == 'invalid api key':
        raise BtceInvalidApiKeyException(error_string)
    else:
        raise BtceApiException(error_string)


class BtceLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        def median(arr):
            arr = sorted(arr)
            return arr[len(arr) / 2 - 1]

        api = BtceApi(self._pubkey, self._privkey, "btc")
        totals = []
        # Query the balance a few times, then grab the median value to work around
        # race conditions in the API.
        for i in range(5):
            availablefunds = api.calculateAvailableFunds()
            orderfunds = api.calculateFundsInOrders()
            totals.append(availablefunds + orderfunds)
        return median(totals)

    def crawl_balance(self):
        api = BtceApi(self._pubkey, self._privkey, "btc")
        wallet = api.calculateTotalWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in list(wallet.items()):
            total += table.convert(k, 'btc', v)
        wallet["Total_BTC"] = total
        return wallet

    def crawl_trades(self):
        api = BtceApi(self._pubkey, self._privkey, "btc")
        start = 0
        size = 1000
        trades = {}
        while True:
            try:
                new_trades = api.getTrades(start, size)
            except BtceNoTradesApiException:
                break

            trades.update(new_trades)
            start += size
            time.sleep(1)  # do not spam
        return trades


class BtceApi:
    def __init__(self, APIKey, Secret, tovalue):
        self.APIKey = str(APIKey).encode("utf-8")
        self.Secret = str(Secret).encode("utf-8")
        self.toValue = tovalue
        self.nonce = int(time.time())
        self.url = 'https://wex.nz'
        self.table = ConversionTable(self.getMarketsGraph())
        
    def query_public(self, uri):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }
        request = urllib.request.Request(self.url + uri, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_private(self, method, uri, req={}):
        req['method'] = method
        req['nonce'] = self.nonce
        post_data = urllib.parse.urlencode(req)
        self.nonce += 1

        sign = hmac.new(self.Secret, post_data.encode("utf-8"), hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': self.APIKey
        }

        request = urllib.request.Request(self.url + uri, headers=headers, data=(urllib.parse.urlencode(req)).encode("utf-8"))
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        reply = json.loads(data)

        throw_btce_exception(reply)
        return reply['return']

    def calculateFundsInOrders(self):
        orders = self._getFundsStuckInOrders()
        total = 0
        if orders is not None:
            for orderid, order in orders.items():
                orderpair = order['pair']
                amount = order['amount']
                keys = orderpair.split('_')
                key = keys[0]
                total += self.table.try_convert(key, self.toValue, amount)
        return total

    def calculateTotalWallet(self):
        funds = self._getWallet()
        orders = self._getFundsStuckInOrders()
        if orders is not None:
            for orderid, order in orders.items():
                orderpair = order['pair']
                amount = order['amount']
                keys = orderpair.split('_')
                key = keys[0]
                funds[keys[0]] = funds[keys[0]] + amount
        return funds

    def _getFundsStuckInOrders(self):
        # calculate funds stuck in orders
        try:
            orders = self.query_private('ActiveOrders', '/tapi')
        except BtceNoOrdersApiException:
            return None
        return orders

    def _getWallet(self):
        wallet = self.query_private('getInfo', '/tapi')
        if wallet is None:
            return wallet
        return wallet['funds']

    def calculateAvailableFunds(self):
        funds = self._getWallet()
        if funds is None:
            return 0
        total = 0
        # calculate funds
        for key, amount in funds.items():
            if amount:
                total += self.table.try_convert(key, self.toValue, amount)
        return total

    def getMarketsGraph(self):
        js = self.query_public('/api/3/info')
        d = {}
        for key, value in js['pairs'].items():
            keys = key.split("_")
            tickerdata = self.getTicker(key)
            pair = (keys[0], keys[1])
            rate = (float(tickerdata['sell']) + float(tickerdata['buy'])) / 2.0
            cost = (float(tickerdata['sell']) - rate) / rate
            d[pair] = (rate, cost)
        return d

    def getTicker(self, pair):
        ret = self.query_public('/api/2/'+pair+'/ticker')
        return ret['ticker']

    def getTrades(self, start, count):
        params = {
            "from": start,
            "count": count,
        }
        return self.query_private('TradeHistory', '/tapi', params)