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

def main():
	# get contents of config file
	config = json-iets...

	# get exchange visitors
	exchangeVisitors = ...

	# get storage manager
	storageManager = ...

	# for each section in config file
	for section in config:
		for visitor in exchangeVisitors:
			if visitor.accepts( section ):
				try:
					info = visitor.visit( section )
					storageManager.write( info, section )
				except Exception as e:
					print str(e)

if __name__ == '__main__':
    main()
