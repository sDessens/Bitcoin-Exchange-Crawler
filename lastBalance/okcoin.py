# Module allows query of balances from OkCoin


import logging
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import hashlib
from common.conversiontable import ConversionTable

log = logging.getLogger('main.exchanges.okcoin')


class OkcoinLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = OkcoinApi(self._pubkey, self._privkey)
        table = self._buildConversionTable(api, True)

        funds = api.query_userinfo()
        total = table.convert('cny', 'btc', float(funds['info']['funds']['asset']['total']))
        return total

    def _buildConversionTable(self, api, is_okcoin_cn):
        if is_okcoin_cn:
            markets = (('btc', 'cny'),
                       ('ltc', 'cny'))
        else:
            markets = (('btc', 'usd'),
                       ('ltc', 'usd'))

        ratios = {}
        for pri, sec in markets:
            js = api.query_ticker('%s_%s' % (pri, sec))
            price = float(js['ticker']['last'])
            ratios[(pri, sec)] = (price, 1)

        return ConversionTable(ratios)


class OkcoinApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)
        self.url = 'https://www.okcoin.cn'

    def post(self, uri, params):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib.request.Request(self.url + uri, data=urllib.parse.urlencode(params), headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def get(self, uri):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib.request.Request(self.url + uri, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_userinfo(self):
        USERINFO_RESOURCE = "/api/v1/userinfo.do"
        params ={}
        params['api_key'] = self.pub
        params['sign'] = self.buildMySign(params)
        return self.post(USERINFO_RESOURCE, params)

    def query_ticker(self, symbol):
        return self.get('/api/v1/ticker.do?symbol=%s' % symbol)

    def buildMySign(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) +'&'
        data = sign+'secret_key=' + self.priv
        return hashlib.md5(data.encode("utf8")).hexdigest().upper()
