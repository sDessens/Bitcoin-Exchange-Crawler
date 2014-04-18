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

""" This functon is required for every PostProcess Visitor module
"""
def getInstance():
    return StubVisitor()


##this is a stub postprocess visitor. It provides an template that provides
# all required functionality for an postprocess visitor
class StubVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #
    def accept( self, json ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    """
    argumant 'data' contains an map 'identifier' -> BalanceData.
    argument 'json' contains implementation defined information about
    the type of processing to do.

    implementation should return post-processed data.
    """
    def visit( self, json, data ):
        return data