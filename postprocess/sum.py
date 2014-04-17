#-------------------------------------------------------------------------------
# Name          sum
# Purpose:      module is post process visitor that allows summing multiple
#               BalanceData objects together.
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import common.balanceData as balanceData

def getInstance():
    return SumVisitor()


class SumVisitor:
    def __init__(self):
        pass

    ##check if the visitor accepts given object
    # @return true of object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'sum'
        except Exception as e:
            return False

    ##run the post process algorithm
    # @param json block of json containing information about the post processing
    # @param data {'identifier' : BalanceData} map
    # @return post-processed {'identifier' : BalanceData} map
    def visit( self, json, data ):
        for k, v in json['data'].items():
            arr = [ data[id] for id in v if id in data ]
            data[k] = balanceData.sum( arr )
        return data