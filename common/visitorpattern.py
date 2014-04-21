#-------------------------------------------------------------------------------
# Name          VisitorPattern
# Purpose:      Module that wraps the Visitor design pattern
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------


class VisitorPattern:
    def __init__( self ):
        self.__visitors__ = []

    """
    Add a visitor to this instance.
    An visitor is any object with an 'accept' method

    @param object vis   the visitor to add
    """
    def addVisitor( self, vis ):
        if not 'accept' in dir(vis):
            raise AssertionError( 'object does not meet minimum requirements of a visitor' )
        self.__visitors__.append( vis )

    """
    Select an visitor that accepts this object,
    or None if no such visitor exists

    @param object obj   the object that the visitor should accept
    """
    def select( self, *arg ):

        for visitor in self.__visitors__:
            if len(arg) == 1:
                if visitor.accept(arg[0]):
                    return visitor
            elif len(arg) == 2:
                if visitor.accept(arg[0]):
                    return visitor
        return None


    def __len__( self ):
        return len( self.__visitors__ )

