#-------------------------------------------------------------------------------
# Name          HtmlReport
# Purpose:      Module is implementation of an process visitor that exports data
#               to a html report with tables.
#
# Author:       Jasper van Gelder
#
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------


import common.balanceData
from common.resources.file import File

from time import time
from datetime import datetime
import logging
log = logging.getLogger( 'main.process.htmlreport' )

## This function is required for every Visitor module
def getInstance():
    return HtmlReportVisitor()

## this is a stub Process visitor. It provides an template that provides
#  all required functionality for an Process visitor
class HtmlReportVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'report'
        except Exception as e:
            return False

    ## run the process algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  may return exception
    def visit( self, json, resources ):
        tmpfile = common.tempFileLib.generateTempFile(True)
        if 'cssfile' in json:
            css = json['cssfile']
        else:
            css = 'htmlExample.css'
        #time variable to use the same time everywhere
        thetime = time()
        htmlgenerator = HmtlReportGenerator( tmpfile,css,json['subject'])
        #process the tables that should be added
        for table in json['tables']:
            #create tabledata with the given period
            tabledata = TableData(float(table['period']),int(table['count']),thetime)
           
            #add the source to the tabledata
            log.info('adding sources to table')
            for source in table['sources']:
                tabledata.addValueRow(resources[source].value,source,table.get('type'))
            tabledata.sort()
            if table.get('totalrow'):
                log.info('adding total row to table')
                tabledata.addTotalRow()
            if table.get('totalcolumn'):
                log.info('adding total column to table')
                tabledata.addDiffTotalColumn()
            log.info('adding tabledata to htmltable')
            htmlgenerator.addTable(tabledata,table['title'],table.get('diffcolors'))
        
        htmlgenerator.finalize()
        
        resources[ json['target'] ] = File( tmpfile )
        return resources
## Class that contains the data for the tables
#  This class contains functions to generate the data for the html table
#  @param period a integer of the interval that each data point should be represented in
#   seconds (period of one day would be 24*60*60)
#  @param periodcount the amount of periods it should process
#  @param thetime the current time from time()
class TableData:
    def __init__(self,period,periodcount,thetime):
        self._period= period
        self._periodcount = periodcount
        self.__table =[]
        self._thetime = thetime
        #add headers to the tables
        self.__table.append(['Source'])
        #add the headers based on date
        for i in reversed(xrange(self._periodcount)):
            datestring = datetime.fromtimestamp(self._thetime - (i * self._period )).strftime('%a')
            self.__table[0].append(datestring)
        
    def addValueRow(self,balancedata,label,diff=None):
        valuerow=[]
        valuerow.append(label)
        if diff == 'diff':
            for i in reversed(xrange(self._periodcount)):
                valuerow.append("%6.3f"%float(balancedata.diff(self._thetime - ((i+1) * self._period),self._thetime - (i* self._period))))
        else:
            for i in reversed(xrange(self._periodcount)):
                valuerow.append("%6.3f"%float(balancedata.interpolate(self._thetime - (i * self._period))))
        self.__table.append(valuerow)
        print valuerow
    
    def addDiffTotalColumn(self):
        #add the label for total column
        self.__table[0].append('Source sum')
        #sum all values
        for row in range(1,len(self.__table)):
            total = sum([float(i) for i in self.__table[row][1:]])            
            self.__table[row].append(total)
        
    def addTotalRow(self):
        self.__table.append(['Period Total'])
        for column in range(1,len(self.__table[0])):
            columntotal=0.0
            for row in range(1,len(self.__table)-1):
                columntotal += float(self.__table[row][column])
            #add the totals to the last row
            self.__table[-1].append("%6.3f"%(columntotal))
            
    def sort(self):
        #sort on suffix
        self.__table.sort(key=lambda s: (s[0]))
    def table(self):
        return self.__table
    def __getitem__(self,key):
        return self.__table[key]
        
## Class generates the html
#  This class contains functions to generate the html report
#  @param tmpFile Requires the fileHandle to write the report to.
#  @param cssFilePath path to the css file that should be used
#  @param title the title that should be used for the report.
class HmtlReportGenerator:
    def __init__(self,tmpFile, cssFilePath,title):
        self.timeformat= '%d/%m/%Y %H:%M:%S'
        self.Html_file = open(tmpFile,"w")
        self.Html_file.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <link rel="stylesheet" type="text/css" href=" """+cssFilePath+""" ">
        <title>"""+title+"""</title>
        <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    </head>
    <body><div id="main">""")

    def addCustomHTML(self,htmldata):
        self.Html_file.write(htmldata)

    ## \brief This function builds a html table from a mulitdimensional array
    # \param tablename the text that should be above the table
    # \param tabledata a multidimensional list of strings first row (tabledata[0]) should contain headers
    # \param diffcolors whether you want to use colors in the table to indicate reduction from the previous period
    def addTable(self,tabledata,tablename,diffcolors=False):
        tableheaders=""
        self.Html_file.write("""
        <div id='"""+tablename+"""' class="entry">
            <table>
            <caption><b>"""+tablename+"""</b></caption>
            <thead><tr>""")
        #Add the headers to the table
        for header in tabledata[0]:
            tableheaders+="<th scope='col'>"+header+"</th>"
        self.Html_file.write(tableheaders+"""</tr></thead>
        <tbody>""")
        #Add the values
        #skip the first key since we already asigned it

        tableiter = iter(tabledata)
        next(tableiter)
        for rowdata in tableiter:
            row = "<tr>"
            for value in rowdata:
                if diffcolors:
                    #if it is a float and the number is negative change color to red if its negative
                    try:
                        if float(value) < 0:
                            row +="<td class='negativevalue'>" + str(value) + "</td>"
                        else:
                            row +="<td class='normalcell'>" + str(value) + "</td>"
                    #if its not a float use normal colors
                    except:
                        row +="<td class='normalcell'>" + str(value) + "</td>"
                else:
                    row +="<td class='normalcell'>" + str(value) + "</td>"
            self.Html_file.write(row + "</tr>")

        self.Html_file.write("""
        </tbody></table></div>""")

    def finalize(self):
        self.Html_file.write("""
        </div>
    </body>
</html>""")
        self.Html_file.close()



