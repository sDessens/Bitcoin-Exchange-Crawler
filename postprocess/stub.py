#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of PostProcess Visitor.
#               Developers can use this file as an example when implementing
#               additional post processing algorithms
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

## This function is required for every Visitor module
def getInstance():
    return StubVisitor()


## this is a stub post-process visitor. It provides an template that provides
#  all required functionality for an post-process visitor
class StubVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    ## run the post-processing algorithm.
    #  @param data an {'identifier' -> BalanceData} map.
    #  @param json contains implementation defined information about the type of processing to do.
    #  @return the post-processed data
    def visit( self, json, data ):
        return data