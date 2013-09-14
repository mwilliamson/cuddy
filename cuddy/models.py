class Model(object):
    def __init__(self, name, fields):
        self._name = name
        self._fields = fields
    

class Field(object):
    def __init__(self, name, type):
        self._name = name
        self._type = type
