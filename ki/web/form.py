import voluptuous
import ki.logg


log = ki.logg.get(__name__)


class FormData:
    def __init__(self, data, errors=None, **kwargs):
        self.data = data
        self.errors = (errors or [])
        self.is_valid = bool(len(self.errors) == 0)

    def get(self, k, default=None):
        return self.data.get(default)

    def __getitem__(self, key):
        return self.data[key]

class Form:
    def __init__(self, d):
        self._values = d

    def get(self, k, default=None):
        return self._values.get(k, default)

    def to_dict(self):
        return self._values

    def validate_schema(self, schema):
        try:
            valid = schema(self._values)
            return FormData(valid)
        except voluptuous.Error as e:
            print(e)
            return FormData(self._values, e.errors)


