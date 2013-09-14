class Model(object):
    def __init__(self, name, fields):
        self._name = name
        self._fields = fields
    

class Field(object):
    def __init__(self, title, getter, type):
        if isinstance(getter, basestring):
            attribute_name = getter
            getter = lambda instance: getattr(instance, attribute_name)
            
        self.title = title
        self._getter = getter
        self._type = type
        
    def short_describe(self, instance):
        value = self._getter(instance)
        value_admin = self._type()
        if hasattr(value_admin, "short_describe"):
            return value_admin.short_describe(value)
        else:
            return str(value)
