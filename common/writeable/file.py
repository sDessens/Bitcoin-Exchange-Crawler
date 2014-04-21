from common.writeable.collection import Resource

class File(Resource):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'File({0})'.format(self.filename)