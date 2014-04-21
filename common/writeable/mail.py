from common.writeable.collection import Resource

class Mail(Resource):
    def __init__(self, subject):
        self.setSubject( 'untitled mail' )
        self.setBody( 'test body' )

    def setSubject(self, subject):
        self.subject = subject

    def setBody(self, body):
        self.body = body

    def addAttachment(self, attachment):
        pass

    def __str__(self):
        assert False, 'not implemented'