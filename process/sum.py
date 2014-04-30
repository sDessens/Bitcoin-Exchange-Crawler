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
from common.writeable.fullBalance import FullBalance

import logging
log = logging.getLogger( 'main.process.sum' )

def getInstance():
    return SumVisitor()

## SumVisitor is an class that allows summing of multiple BalanceData objects.
class SumVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'sum'
        except Exception as e:
            return False

    ## run the process algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  @return the full, post-processed, list of resources
    #  may return exception
    def visit( self, json, resources ):
        for key, inputs in json['data'].items():
            try:
                resources[key] = self._sumBalance( resources, inputs )
            except Exception as e:
                log.error( e )
                pass

        return resources


    def _sumBalance(self, resources, inputs):
        arr = []

        for input in inputs:
            if input in resources:
                res = resources[input]
                if isinstance( res, FullBalance ):
                    arr.append( res.value )
                else:
                    print 'resource named', input, 'of incorrect type'

        if len(arr) == 0:
            raise Exception( 'No resources of {0} found'.format(inputs) )

        return FullBalance( balanceData.sum( arr ) )