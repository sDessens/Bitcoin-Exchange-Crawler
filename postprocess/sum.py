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

## SumVisitor is an class that allows summing of multiple BalanceData objects.
class SumVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'sum'
        except Exception as e:
            return False

    ## run the post-processing algorithm.
    #  @param data an {'identifier' : BalanceData} map.
    #  @param json contains implementation defined information about the type of processing to do.
    #  @return the post-processed data
    def visit( self, json, data ):
        for k, v in json['data'].items():
            arr = [ data[id] for id in v if id in data ]
            if len(arr) > 0:
                data[k] = balanceData.sum( arr )
        return data