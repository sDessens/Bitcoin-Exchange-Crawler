# Module allows query of recent bitcoin prices from coinmarketcap api

import json
import urllib2
import logging

log = logging.getLogger("main.exchanges.coinmarketcap")


class CoinMarketcapLastBalance:
    def __init__(self, symbol):
        self._symbol = symbol

    def crawl(self):
        api = CoinMarketcapApi()
        tickers = api.query_tickers()

        for ticker in tickers:
            if ticker["symbol"] == self._symbol:
                return ticker["price_usd"]

        log.error("could not find symbol %s" % self._symbol)
        raise ValueError("could not find symbol %s" % self._symbol)


class CoinMarketcapApi:
    def __init__(self):
        self.url = "https://api.coinmarketcap.com"

    def get(self, uri):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode("utf-8")
        return json.loads(data)

    def query_tickers(self):
        return self.get("/v1/ticker/")
