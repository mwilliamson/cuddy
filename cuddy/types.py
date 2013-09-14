class StringAdmin(object):
    def short_describe(self, value):
        return value


class DateTimeAdmin(object):
    def short_describe(self, value):
        return str(value)
