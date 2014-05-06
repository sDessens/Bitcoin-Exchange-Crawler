# This module implements SMTP to send reports via mail. the
# 'remote' parts refers to the fact this implementation uses
# remote SMTP servers such as google's one.


from common.resources.mail import Mail
import smtplib
import logging
log = logging.getLogger( 'main.write.remoteSMTP' )


def getInstance():
    return RemoteSMTPVisitor()


## this is a stub write visitor. It provides an template that provides all
#  required functionality for an storage visitor
class RemoteSMTPVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'remotesmtp'
        except Exception as e:
            return False

    def visit(self, json, resources):
        server = json['server']
        port = json['port']
        username = json['username']
        password = json['password']
        to = json['to']
        data = json['data']

        client = SMTPClient( server, port, username, password )

        for key in data:
            try:
                resource = resources[key]
                if not isinstance(resource, Mail):
                    log.error( 'resource {0} is not of type Mail'.format(key) )
                    continue
                try:
                    client.sendmail( resource, to )
                except Exception as e:
                    log.error( str(e) )
            except:
                log.error( 'unable to find resource {0}'.format(key) )


class SMTPClient:
    def __init__(self, server, port, username, password):
        self.sender = username

        self.smtp = smtplib.SMTP( server, port )
        self.smtp.starttls()
        self.smtp.login( username, password )

    def sendmail(self, mail, to):
        assert( isinstance(mail, Mail) )
        self.smtp.sendmail( self.sender,
                            to,
                            "Subject: {0}\n\n{1}".format( mail.subject, mail.body ) )
