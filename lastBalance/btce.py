# Module allows the retrieval of balances from BTC-e

import urllib
from urllib3 import connection_from_url
import json
import hmac
import time
import hashlib
from common.conversiontable import ConversionTable, ConversionException
import logging

log = logging.getLogger('main.read.btce')



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
        for i in range(3):
            availablefunds = api.calculateAvailableFunds()
            orderfunds = api.calculateFundsInOrders()
            totals.append(availablefunds + orderfunds)
        return median(totals)


class BtceApi:
    def __init__(self, APIKey, Secret, tovalue):
        self.APIKey = str(APIKey)
        self.Secret = str(Secret)
        self.toValue = tovalue
        self.nonce = int(time.time())
        self.url = 'https://btc-e.com'
        self.table = ConversionTable(self.getMarketsGraph())
        
    def query_public(self, uri):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
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
            'Key': self.APIKey
        }

        request = urllib2.Request(self.url + uri, headers=headers, data=urllib.urlencode(req))
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        reply = json.loads(data)

        # raise an error if it is an invalid key
        if int(reply['success']) == 1:
            return reply['return']

        if reply['error'] == 'invalid api key':
            raise Exception('Btce: ' + str(reply['error']))
        elif reply['error'] == 'no orders':
            return None

    def calculateFundsInOrders(self):
        # calculate funds stuck in orders
        total = 0
        orders = self.query_private('ActiveOrders','/tapi')
        if orders is not None:
            for orderid, order in orders.iteritems():
                orderpair = order['pair']
                amount = order['amount']
                keys = orderpair.split('_')
                key = keys[0]
                total += self.table.try_convert(key, self.toValue, amount)
        return total

    def calculateAvailableFunds(self):
        wallet = self.query_private('getInfo', '/tapi')
        if wallet is None:
            return 0

        funds = wallet['funds']
        total = 0
        # calculate funds
        for key, amount in funds.iteritems():
            if amount:
                total += self.table.try_convert(key, self.toValue, amount)
        return total

    def getMarketsGraph(self):
        js = self.query_public('/api/3/info')
        d = {}
        for key, value in js['pairs'].iteritems():
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
