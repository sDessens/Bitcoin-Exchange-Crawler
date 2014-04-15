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

import visitorpattern
import exchanges

def main():

	# get all visitors for exchanges
	exchangeVisitors = visitorpattern.VisitorPattern()

	for item in exchanges.__all__:
		module = __import__( 'exchanges.' + item )
		attr = getattr( module, item )
		try:
			exchangeVisitors.addVisitor( attr.getInstance() )
		except Exception as e:
			if type(e) is AssertionError:
		 		print str(e)
			else:
				print 'unable to add exchange visitor for module {0}.py'\
				.format( item )

	"""

	# get contents of config file
	config = json-iets...

	# get exchange visitors
	exchangeVisitors = ...

	# get storage manager
	storageManager = ...

	# for each section in config file
	for section in config:
		visitor = exchangeVisitors.select( section )
		if visitor != None:
			try:
				info = visitor.visit( section )
				storageManager.write( info, section )
			except Exception as e:
				print str(e)
		else:
			print 'no visitor could be found that accepts', section

	"""

if __name__ == '__main__':
    main()
