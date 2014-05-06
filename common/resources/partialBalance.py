# this module implements an resource that holds a single balance.
# visitors that read balanced from an exchange return this type of resource.


from common.resources.collection import Resource

class PartialBalance(Resource):
    def __init__(self, value):
        assert isinstance( value, float )
        self.value = value

    def __str__(self):
        return 'PartialBalance({0})'.format(self.value)
