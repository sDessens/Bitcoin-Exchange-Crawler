#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Stefan
#
# Created:     15-04-2014
# Copyright:   (c) Stefan 2014
# Licence:     <your licence>
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
		self.__visitors__.append( vis );
		if not 'accept' in dir(vis):
			raise AssertionError( 'visitor could not be added, ' +
				'because the object does not meet the minimum ' +
				'requirements of a visitor' )

	"""
	Select an visitor that accepts this object,
	or None if no such visitor exists

	@param object obj   the object that the visitor should accept
	"""
	def select( self, obj ):
		for visitor in self.__visitors__:
			if visitor.accept( obj ):
				return visitor
		return None

