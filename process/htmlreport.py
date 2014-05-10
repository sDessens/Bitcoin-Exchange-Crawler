# Purpose:      Module is implementation of an process visitor that exports data

from common.resources.fullBalance import FullBalance
from common.balanceData import BalanceData
from common.resources.file import File
from common.resources.report import Report
import common.parsevisitorsfromfolder as pv

from time import time
from os import pathsep
from datetime import datetime
import logging
log = logging.getLogger( 'main.process.htmlreport' )

## This function is required for every Visitor module
def getInstance():
    return HtmlReportVisitor()

## this is a Process visitor. It provides all required functionality 
#  for an Process visitor
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

    ## run the htmlreport process.
    #  this visitor adds a html file to resources
    #  
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.resources.fullBalance.FullBalance
    def visit( self, json, resources ):
        out = Report( json['subject'] )

        if 'cssfile' in json:
            css = json['cssfile']
        else:
            css = 'default report.css'
        #time variable to use the same time everywhere
        thetime = time()
        htmlgenerator = HmtlReportGenerator( open(css, 'r').read(), json['subject'] )
        #process the kpis
        if json.get('kpis'):
            kpiVisitors = pv.getVisitorsFromFolder( 'kpis' )
            #create the multidimensional list later to be used to create the table
            kpilist = [["KPI","","Value"]]
            for kpi in json['kpis']:
                visitor = kpiVisitors.select( kpi)
                if visitor is None:
                    log.error( 'no read visitor could be found for kpi {0}'.format( kpi ) )
                    continue
                try:
                    #visit the kpi and fetch the value
                    indicator, kpivalue = visitor.visit( kpi,resources )
                    name = kpi['name']
                    kpilist.append([name,indicator,"%6.3f"%kpivalue]) 
                except Exception as e:
                    log.error( 'an exception occurred when visiting {0}: {1}'.format( visitor.__class__.__name__, str(e) ) )      
            htmlgenerator.addTable(kpilist,"KPI table")
                
        #process the tables that should be added
        for table in json['tables']:
            #create tabledata with the given period
            tabledata = TableData(float(table['period']),int(table['count']),thetime)
           
            #add the source to the tabledata
            log.info('adding sources to table')
            balanceCollection = resources.selectMany(table['sources'],FullBalance)
            #if no resources are found skip to the next table
            if len(balanceCollection) <1:
                log.warn('No resources found to add to table')
                continue
            for key, resource in balanceCollection:
                tabledata.addValueRow(resource.value,key,table.get('type'))
            
            tabledata.sort()
            #add the total row and column if the options are set
            if table.get('totalrow'):
                log.info('adding total row to table')
                tabledata.addTotalRow()
            if table.get('totalcolumn'):
                log.info('adding total column to table')
                tabledata.addDiffTotalColumn()
            log.info('adding tabledata to htmltable')
            htmlgenerator.addTable(tabledata,table['title'],table.get('diffcolors'))
            
        htmlgenerator.finalize()

        out.setBody( htmlgenerator.body )
        resources[ json['out'] ] = out
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
        #determine the header format to be used
        if period < (24*60*60):
            headerformat = '%H:%M'
            if periodcount > 24:
                headerformat = '%a ' + headerformat
        elif period < (7*24*60*60):
            headerformat = '%a'
            if periodcount > 7:
                headerformat += ' %x'
        else:
            headerformat =  '%x'
        #add the headers based on date
        for i in reversed(xrange(self._periodcount)):
            datestring = datetime.fromtimestamp(self._thetime - (i * self._period )).strftime(headerformat)
            self.__table[0].append(datestring)
    ## This function should be used to add rows to the table.
    # @param balancedata requires balancedata
    # @label the label for the row
    # @valuetype string with the given type (currently only diff is implemented)
    def addValueRow(self,balancedata,label,valuetype=None):
        if not isinstance(balancedata,BalanceData):
            log.warn('incorrect source type')
            return
        valuerow=[]
        valuerow.append(label)
        if valuetype == 'diff':
            for i in reversed(xrange(self._periodcount)):
                valuerow.append("%6.3f"%float(balancedata.diff(self._thetime - ((i+1) * self._period),self._thetime - (i* self._period))))
        else:
            for i in reversed(xrange(self._periodcount)):
                valuerow.append("%6.3f"%float(balancedata.interpolate(self._thetime - (i * self._period))))
        self.__table.append(valuerow)

    ## This function adds a total column.
    # It sums up each row and adds the value to the end of the row
    def addDiffTotalColumn(self):
        #add the label for total column
        self.__table[0].append('Source sum')
        #sum all values
        for row in range(1,len(self.__table)):
            total = sum([float(i) for i in self.__table[row][1:]])            
            self.__table[row].append("%6.3f"%total)
    ## This function adds a totalRow below the last row    
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
        
## This class contains functions to generate the html report
#  @param tmpFile Requires the fileHandle to write the report to.
#  @param cssFilePath path to the css file that should be used
#  @param title the title that should be used for the report.
class HmtlReportGenerator:
    def __init__(self, css, title):
        self.body = ""
        self.addCustomHTML("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html;charset=utf-8" />
        <style media="screen" type="text/css">
        """+css+"""
        </style>
        <title>"""+title+"""</title>
    </head>
    <body><div id="main">""")
        
    ## This function adds any data you want in your html file
    # @param htmldata the data you whish to insert
    def addCustomHTML(self,htmldata):
        self.body += htmldata

    ## \brief This function builds a html table from a mulitdimensional array
    # \param tablename the text that should be above the table
    # \param tabledata a multidimensional list of strings first row (tabledata[0]) should contain headers
    # \param diffcolors whether you want to use colors in the table to indicate reduction from the previous period
    def addTable(self,tabledata,tablename,diffcolors=False):
        tableheaders=""
        self.addCustomHTML("""
        <div id='"""+tablename+"""' class="entry">
            <table>
            <caption><b>"""+tablename+"""</b></caption>
            <thead><tr>""")
        #Add the headers to the table
        for header in tabledata[0]:
            tableheaders+="<th scope='col'>"+header+"</th>"
        self.addCustomHTML(tableheaders+"""</tr></thead>
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
            self.addCustomHTML(row + "</tr>")

        self.addCustomHTML("""
        </tbody></table></div>""")
    ## This function closes the html tags and file
    def finalize(self):
        self.addCustomHTML("""
        </div>
    </body>
</html>""")



