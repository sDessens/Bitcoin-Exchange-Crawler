# This module implements SMTP to send reports via mail. the
# 'remote' parts refers to the fact this implementation uses
# remote SMTP servers such as google's one.


from common.resources.report import Report
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import premailer
import traceback
import logging
log = logging.getLogger( 'main.write.SMTP' )


def getInstance():
    return SMTPVisitor()


## this is a stub write visitor. It provides an template that provides all
#  required functionality for an storage visitor
class SMTPVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'smtp'
        except Exception as e:
            return False

    def visit(self, json, resources):
        server = json['server']
        port = json['port'] if 'port' in json else 587
        consec = json['connection-security']
        authtype = json['auth-type']
        username = json['username']
        password = json['password'] if 'password' in json else ''
        to = json['to']
        data = json['data']
        
        client = SMTPClient( server, port, username, password,consec,authtype )

        for key in data:
            try:
                resource = resources[key]
                if not isinstance(resource, Report):
                    log.error( 'resource {0} is not of type Report'.format(key) )
                    continue
                try:
                    client.sendmail( resource, to )
                except Exception as e:
                    log.error( str(e) )
                    log.debug( traceback.format_exc() )
            except:
                log.error( 'unable to find resource {0}'.format(key) )


class SMTPClient:
    def __init__(self, server, port, username, password,connsec,authtype):
        self.sender = username

        if connsec == "starttls":
            self.smtp = smtplib.SMTP( server, port )
            self.smtp.starttls()
        elif connsec == "ssltls":
            self.smtp = smtplib.SMTP_SSL( server, port )
        elif connsec == "none":
            self.smtp = smtplib.SMTP( server,port )
        else:
            #no method selected defaulting to starttls for security reasons
            self.smtp = smtplib.SMTP( server, port )
            self.smtp.starttls()
        if authtype == "ntlm":
            pass
        elif authtype  == "plain":
            self.smtp.login( username, password ) 
            

    def sendmail(self, mail, to):
        assert( isinstance(mail, Report) )
        msg = MIMEMultipart('alternative')
        msg['Subject'] = mail.subject
        msg['From'] = self.sender
        msg['To'] = ", ".join(to)

        msg.attach( MIMEText( premailer.transform(mail.body), 'html') )
        self.smtp.sendmail( self.sender, to, msg.as_string() )
