# Module allows the retrieval of balances from BtcChina

import json
import urllib
import urllib2
import time
import hashlib
import hmac
import base64
import logging
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.itbit' )

def getInstance():
    return ItbitVisitor()

class ItbitVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'itbit'
        except Exception as e:
            return False

    def visit( self, json ):
        api = ItbitApi( json['pubkey'], json['privkey'], json['userid'] )
        out = Collection()
        wallet = api.getWallet(json['walletid'])
        if wallet != None:
            table = ConversionTable(api.getMarketsGraph())
            total = 0

            for k, v in wallet.items():
                total += table.convert(k, 'XBT', v)
            log.debug("total: " + str(total))
            out[json['out']] = PartialBalance( total )
        return out

#Most is taken from http://api-portal.anypoint.mulesoft.com/itbit/api/itbit-exchange/docs/code
class ItbitApi:
    def __init__(self, pub, priv,userid):
        self.clientKey = str(pub)
        self.secret = str(priv)
        self.userId = userid
        self.nonce = 0

    def make_request(self, verb, url, body_dict):
        url = 'https://api.itbit.com/v1' + url
        nonce = self._get_next_nonce()
        timestamp = self._get_timestamp()

        if verb in ("PUT", "POST"):
            json_body = json.dumps(body_dict)
        else:
            json_body = ""

        signer = MessageSigner()
        signature = signer.sign_message(self.secret, verb, url, json_body, nonce, timestamp)

        auth_headers = {
            'Authorization': self.clientKey + ':' + signature,
            'X-Auth-Timestamp': timestamp,
            'X-Auth-Nonce': nonce,
            'Content-Type': 'application/json'
        }
        if json_body == "":
            req = urllib2.Request(url=url, headers=auth_headers)
        else:
            req = urllib2.Request(url=url, data=json_body, headers=auth_headers)
        try:
            response = urllib2.urlopen(req)
            r = json.loads(response.read())
        except urllib2.HTTPError as e:
            error = json.loads(e.read())
            log.error("httpstatus: " + str(e.code) + " code: " + str(error['code']) + " message: " + error['message'])
            r = None
        return r

    def get_all_wallets(self, filters={}):
        filters['userId'] = self.userId
        queryString = self._generate_query_string(filters)
        path = "/wallets%s" % (queryString)
        response = self.make_request("GET", path, {})
        return response

    def get_wallet(self, walletId):
        path = "/wallets/%s" % (walletId)
        response = self.make_request("GET", path, {})
        return response

    def getWallet(self, walletId):
        js = self.get_wallet(walletId)
        wallet = {}
        if js != None:
            for balance in js['balances']:
                k = balance['currency']
                v = float(balance['totalBalance'])
                wallet[k] = v
        else:
            wallet = None
        return wallet

    def getMarkets(self):
        # Also for Itbit. Please fix your api.
        return [
            ('XBT', 'USD'),
            ('XBT', 'SGD'),
            ('XBT', 'USD'),
            ('XBT', 'EUR'),
        ]

    def _get_public(self, www, uri):
        req = urllib2.Request(www + uri)
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib2.urlopen(req).read())

    def getMarketsGraph(self):
        graph = {}
        www = 'https://api.itbit.com'
        for pri, sec in self.getMarkets():
            uri = '/v1/markets/%s%s/ticker' % (pri, sec)
            js = self._get_public(www, uri)
            bid = float(js['bid'])
            ask = float(js['ask'])
            avg = (bid + ask) / 2
            diff = abs(bid - ask) / avg
            graph[(pri, sec)] = (avg, diff)
        return graph

    def _get_next_nonce(self):
        self.nonce += 1
        return self.nonce


    def _get_timestamp(self):
        return int(time.time() * 1000)
    def _generate_query_string(self, filters):
        if filters:
            return '?' + urllib.urlencode(filters)
        else:
            return ''

class MessageSigner(object):

    def make_message(self, verb, url, body, nonce, timestamp):
        # Need to specify that there should be no spaces after separators
        return json.dumps([verb, url, body, str(nonce), str(timestamp)], separators=(',',':'))

    def sign_message(self, secret, verb, url, body, nonce, timestamp):
        message = self.make_message(verb, url, body, nonce, timestamp)
        sha256_hash = hashlib.sha256()
        nonced_message = str(nonce) + message
        sha256_hash.update(nonced_message)
        hash_digest = sha256_hash.digest()
        hmac_digest = hmac.new(secret, url.encode('utf8') + hash_digest, hashlib.sha512).digest()

        return base64.b64encode(hmac_digest)
