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
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    ## run the export algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param json contains implementation defined information about the export type
    #  @param resources contains array of common.writable.*
    #  @return the full, post-processed, list of resources
    #  may return exception
    def visit( self, json, resources ):
        print 'begin of stub export visitor output'
        for resource in resources:
            print '   ', str(resource)
        print 'end of stub export visitor output'

        # this stub visitor doesn't actually add resources.
        # if you're writing your own export visitor, take a look at how sum.py handles stuff
        return resources