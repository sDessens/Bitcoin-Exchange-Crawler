#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of Export Visitor.
#               Developers can use this file as an example when implementing
#               additional exporters
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

## this is a stub Export visitor. It provides an template that provides
#  all required functionality for an Export visitor
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

    ## run the export algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param data an {'identifier' : BalanceData} map.
    #  @param json contains implementation defined information about the export type
    #  @param write an {'identifier' : Writedb} map.
    #  @return some sort of file array
    def visit( self, json, data, writedb ):
        print 'begin of stub export visitor output'
        for k, v in data.items():
            print '  {0:15s} = {1}'.format(k, v.interpolate( v.maxTimestampAsDateTime() ) )
        print 'end of stub export visitor output'
        return []