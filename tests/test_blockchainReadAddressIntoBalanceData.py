from unittest import TestCase

__author__ = 'Stefan'

import read.blockchain as blockchain
import common.balanceData as balanceData
from dateutil import parser
import logging
import json


class TestBlockchainReadAddressIntoBalanceData(TestCase):
    def test_parse(self):
        FORMAT = "%(asctime)-15s %(levelname)s %(name)s: %(message)s"
        logging.basicConfig(format=FORMAT)


        example_reponse = """{
                            "hash160":"b5299ca65ea259087a1a25c816d9f718965e397c",
                            "address":"1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2",
                            "n_tx":3,
                            "total_received":274880000,
                            "total_sent":74940000,
                            "final_balance":199940000,
                            "txs":[{"result":0,"block_height":296050,"time":1397599146,"inputs":[{"prev_out":{"n":0,"value":2320000,"addr":"1Mg8phYn4RsempHdfDrJWeSsGQ874XFQ2c","tx_index":54601864,"type":0,"script":"76a914e2c9449b4b346a818a98322fc9d373067334bed488ac"},"script":"76a914e2c9449b4b346a818a98322fc9d373067334bed488ac"},{"prev_out":{"n":1,"value":100000000,"addr":"1HC3dc4DubRat1P39YBBkwVRbph3ijbtPQ","tx_index":54593715,"type":0,"script":"76a914b198c8d267a0840436bfb076ac0e6ca1ede09d1288ac"},"script":"76a914b198c8d267a0840436bfb076ac0e6ca1ede09d1288ac"},{"prev_out":{"n":0,"value":100000000,"addr":"1HC3dc4DubRat1P39YBBkwVRbph3ijbtPQ","tx_index":54595895,"type":0,"script":"76a914b198c8d267a0840436bfb076ac0e6ca1ede09d1288ac"},"script":"76a914b198c8d267a0840436bfb076ac0e6ca1ede09d1288ac"}],"vout_sz":2,"relayed_by":"50.31.99.225","hash":"2800eb333806565044ce5d50003826049b19337a5b84d8689571a35c29062db4","vin_sz":3,"tx_index":54602143,"ver":1,"out":[{"n":0,"value":199940000,"addr":"1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2","tx_index":54602143,"spent":true,"type":0,"script":"76a914b5299ca65ea259087a1a25c816d9f718965e397c88ac"},{"n":1,"value":2370000,"addr":"1MobSB3Thv7XQXUHGbDV9uJyRDPwR548w6","tx_index":54602143,"spent":false,"type":0,"script":"76a914e43264dc87568a28e3e13e7d46fb23a7cf47f8b588ac"}],"size":521},{"result":199940000,"block_height":293287,"time":1396214174,"inputs":[{"prev_out":{"n":1,"value":74940000,"addr":"1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2","tx_index":51999557,"type":0,"script":"76a914b5299ca65ea259087a1a25c816d9f718965e397c88ac"},"script":"76a914b5299ca65ea259087a1a25c816d9f718965e397c88ac"}],"vout_sz":2,"relayed_by":"192.241.205.107","hash":"16ab30c04015bb9aaec7f34611abb92bdb94c69607345ee6f752ba90c0203358","vin_sz":1,"tx_index":53578139,"ver":1,"out":[{"n":0,"value":73920000,"addr":"1oNpg73QWwqSrC5CZHg3Z8dDKKqTNJwvg","tx_index":53578139,"spent":true,"type":0,"script":"76a91408c559ad930773984e49097b0757357bd559531d88ac"},{"n":1,"value":1000000,"addr":"16ZKWgz6YdKQYHArBRrDsTBRa9eUhgvZ65","tx_index":53578139,"spent":false,"type":0,"script":"76a9143cf5648413f07f6d36b2f23101f4cfbf1876376588ac"}],"size":259},{"result":-74940000,"block_height":289608,"time":1394320580,"inputs":[{"prev_out":{"n":1,"value":78080000,"addr":"1Kpzv8YQ3wPvSN91JhPLwjXiKVVLQ7xHGB","tx_index":51997559,"type":0,"script":"76a914ce862901c6509c9a8173f6ccefc13708367d6d1288ac"},"script":"76a914ce862901c6509c9a8173f6ccefc13708367d6d1288ac"}],"vout_sz":2,"relayed_by":"0.0.0.0","hash":"e55054c5b2a4ed51f3cc259236994fed0d3aac43192ea68fca98567da33ca22d","vin_sz":1,"tx_index":51999557,"ver":1,"out":[{"n":0,"value":3110000,"addr":"1H15j5RMNWdUasQRMuh1iykyQS5uwad5RS","tx_index":51999557,"spent":false,"type":0,"script":"76a914af85f507b6be175b2ecc6c60dce4711ce22de36f88ac"},{"n":1,"value":74940000,"addr":"1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2","tx_index":51999557,"spent":false,"type":0,"script":"76a914b5299ca65ea259087a1a25c816d9f718965e397c88ac"}],"size":227}]
                            }"""

        bc = blockchain.BlockchainReadAddressIntoBalanceData()

        # test using response shown above
        bd =  bc._parse( '1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2', json.loads(example_reponse) )
        self.assertIsInstance( bd, balanceData.BalanceData )
        self.assertAlmostEqual( bd.interpolate( parser.parse("Aug 28 1999 12:00") ), 0, 3)
        self.assertAlmostEqual( bd.interpolate( parser.parse("Mar 10 2014 12:00") ), 0.7494, 3 )
        self.assertAlmostEqual( bd.interpolate( parser.parse("Apr 18 2014 12:00") ), 1.9994, 3 )

        # test using real API
        bd = bc.query_address( '1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2' )
        self.assertIsInstance( bd, balanceData.BalanceData )
        self.assertAlmostEqual( bd.interpolate( parser.parse("Aug 28 1999 12:00") ), 0, 3)
        self.assertAlmostEqual( bd.interpolate( parser.parse("Mar 10 2014 12:00") ), 0.7494, 3 )
        self.assertAlmostEqual( bd.interpolate( parser.parse("Apr 18 2014 12:00") ), 1.9994, 3 )





