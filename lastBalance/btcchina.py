# Module allows the retrieval of balances from BtcChina

import json
import urllib.request, urllib.error, urllib.parse
import time
import hashlib
import hmac
import base64
import logging
from common.conversiontable import ConversionTable

log = logging.getLogger('main.exchanges.btcchina')


class BtcChinaLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BtcChinaApi(self._pubkey, self._privkey)
        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in list(wallet.items()):
            total += table.convert(k, 'BTC', v)
        return total

class BtcChinaApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def _getAuthenticated(self, url, method, params):
        thetonce = self.tonce()
        signparms = ""
        for param in params:
            if signparms != "":
                signparms += ','
            if param == True:
                signparms += '1'
            elif param == False:
                continue
            else:
                signparms += param

        signdata = "tonce=" + str(thetonce) \
                + "&accesskey=" + self.pub \
                + "&requestmethod=post&id=2" \
                + "&method=" + method \
                + "&params=" + signparms
        sign = hmac.new(self.priv, signdata, hashlib.sha1).digest().encode('hex')
        postdata = {}
        postdata['tonce'] = thetonce
        postdata['accesskey'] = self.pub
        postdata['requestmethod'] = 'post'
        postdata['id'] = 2
        postdata['method'] = method
        postdata['params'] = params

        headers = {
            'Authorization': "Basic " + base64.b64encode(self.pub + ":" + sign),
            'Json-Rpc-Tonce': thetonce
        }
        ret = urllib.request.urlopen(urllib.request.Request(url, json.dumps(postdata), headers))
        return json.loads(ret.read())


    def getWallet(self):
        js = self._getAuthenticated('https://api.btcchina.com/api_trade_v1.php', 'getAccountInfo', ['ALL'])["result"]
        d = {}
        for payload in list(js['balance'].values()):
            k = payload['currency']
            v = float(payload['amount'])
            d[k] = v
        for payload in list(js['frozen'].values()):
            k = payload['currency']
            v = float(payload['amount'])
            d[k] += v
        return d

    def getMarketsGraph(self):
        ret = urllib.request.urlopen(urllib.request.Request('https://data.btcchina.com/data/ticker?market=all'))
        js = json.loads(ret.read())
        d = {}
        for key, payload in list(js.items()):
            marketcode = str(key).split("_")[1]
            pair = (marketcode[:3].upper(),marketcode[-3:].upper())
            print(pair)
            rate = float(payload['last'])
            cost = 1/float(payload['vol'])
            d[pair] = (rate, cost)
        return d

    def tonce(self):
        return int(time.time()*1000000)
