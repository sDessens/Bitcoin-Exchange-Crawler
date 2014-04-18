#-------------------------------------------------------------------------------
# Name          LocalFileStorage
# Purpose:      Module that provides functionallity to write/read files and
#               balancedata to/from local file storage.
#
# Author:       Jasper van Gelder
#
# Created:      17-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------
import os
import time
from common.balanceData import BalanceData

##
#This class uses local storage as medium.
#
# @param location the dropbox folder the files should be send to
# \var self.seperator the separator used for the uploaded files
# All params should be string values
# Example:
#   storage = LocalFileStorage('/mysubfolder')
#   this will store the files in mysubfolder with values separated by ','
  
class LocalFileStorage:
    def __init__(self,location):
        self.location = location
        self.separator = ","
        
    ##The write function that adds the balance value to the file in the given folder
    # @param identifier a string that identifies the file it will be written to.
    # @param value the value that should be writen
    def writeBalance(self, identifier, value):
        timestamp = int(time.time())
        filename = '/'+identifier+'.csv'
        try:
            with open(self.location+filename, mode='a') as fp:
                fp.write(str(timestamp) +self.separator+str(value))
        except:
            print "creating file"
            with open(self.location+filename, mode='w') as fp:
                fp.write(str(timestamp) +self.separator+str(value))

    ##The read function that downloads the balancedata and returns a BalanceData object
    # @param identifier a string that identifies the file it will be written to.
    # @param fromTime the timeStamp from which the data should be returned
    # @param toTime the until what timeStamp data should be fetched
    # @return BalanceData the object that contains the balance data and timestamp in the period given by fromTime,toTime
    def readBalance(self, identifier, fromTime=0,toTime=int(0xFFFFFFFFFF)):
        timestamps = []
        balance = []
        
        filename = '/'+identifier+'.csv'
        try:
            with open(self.location+filename, mode='r') as fp:
                for line in fp:
                    values = line.split(self.separator)
                    time = int(values[0])
                    if  time > fromTime and time < toTime:
                        timestamps.append(time)
                        balance.append(float(values[1]))
                return BalanceData(timestamps,balance)
        except Exception as e:
            print e
            print "No data for this section found"
    ##  Reads a file from local storage
    #   @param identifier the name of the file
    #   @return returns the data from file
    def readFile(self, identifier):
        try:
            with open(self.location+'/'+identifier, mode='r') as fp:
                return fp.read()
        except:
            raise
    ##  Writes the file to local storage
    #   @param filepointer
    #   @param uploadname the name underwhich to upload the file
    #   @param overwrite bool if the file should be overwriten or not
    #   \exception OSError: File exists if overwrite = False and the file already exists
    def writeFile(self, filepointer,identifier,overwrite=True):
        if overwrite:
            try:
                with open(self.location+identifier, mode='w') as fp:
                    fp.write(filepointer.read())
            except:
                raise
        else:
    #taken from http://stackoverflow.com/a/1348073
            try:
                with os.open(self.location+identifier, os.O_WRONLY | os.O_CREAT | os.O_EXCL) as fd:
                    f = os.fdopen(fd)  # f is now a standard Python file object
                    f.write(filepointer.read())
            except:
                raise
