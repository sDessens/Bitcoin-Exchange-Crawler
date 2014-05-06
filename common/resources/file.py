# this module defines an resource that can be used to pass files between different visitors.


from common.resources.collection import Resource

class File(Resource):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'File({0})'.format(self.filename)