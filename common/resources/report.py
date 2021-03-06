# this module implements an resource that is used to pass reports
# between different visitors.

from common.resources.collection import Resource

class Report(Resource):
    def __init__(self, subject):
        self.setSubject( subject )
        self.setBody( 'default mail body' )

    def setSubject(self, subject):
        self.subject = subject

    def setBody(self, body):
        self.body = body

    def addAttachment(self, attachment):
        pass

    def __str__(self):
        return 'Report({0}, {1})'.format(self.subject, hex(id(self)))
