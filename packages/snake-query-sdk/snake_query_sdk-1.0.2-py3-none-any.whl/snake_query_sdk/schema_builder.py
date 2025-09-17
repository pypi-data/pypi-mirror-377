class SchemaBuilder:
    def __init__(self):
        self.schema = {}

    def object(self, properties=None):
        self.schema = {
            'type': 'object',
            'properties': properties or {}
        }
        return self

    def array(self, item_schema=None):
        self.schema = {
            'type': 'array',
            'items': item_schema or {'type': 'object'}
        }
        return self

    def string(self, **kwargs):
        self.schema = {'type': 'string', **kwargs}
        return self

    def number(self, **kwargs):
        self.schema = {'type': 'number', **kwargs}
        return self

    def integer(self, **kwargs):
        self.schema = {'type': 'number', **kwargs}
        return self

    def boolean(self):
        self.schema = {'type': 'boolean'}
        return self

    def add_property(self, name, schema):
        if 'properties' not in self.schema:
            self.schema['properties'] = {}
        self.schema['properties'][name] = schema
        return self

    def add_string_property(self, name, **kwargs):
        return self.add_property(name, {'type': 'string', **kwargs})

    def add_number_property(self, name, **kwargs):
        return self.add_property(name, {'type': 'number', **kwargs})

    def add_integer_property(self, name, **kwargs):
        return self.add_property(name, {'type': 'number', **kwargs})

    def add_boolean_property(self, name):
        return self.add_property(name, {'type': 'boolean'})

    def add_array_property(self, name, item_schema=None):
        return self.add_property(name, {
            'type': 'array',
            'items': item_schema or {'type': 'string'}
        })

    def add_object_property(self, name, properties=None):
        return self.add_property(name, {
            'type': 'object',
            'properties': properties or {}
        })

    def required(self, fields):
        self.schema['required'] = fields if isinstance(fields, list) else [fields]
        return self

    def add_required(self, field):
        if 'required' not in self.schema:
            self.schema['required'] = []
        if field not in self.schema['required']:
            self.schema['required'].append(field)
        return self

    def description(self, desc):
        self.schema['description'] = desc
        return self

    def enum(self, values):
        self.schema['enum'] = values
        return self

    def minimum(self, min_val):
        self.schema['minimum'] = min_val
        return self

    def maximum(self, max_val):
        self.schema['maximum'] = max_val
        return self

    def min_length(self, min_len):
        self.schema['minLength'] = min_len
        return self

    def max_length(self, max_len):
        self.schema['maxLength'] = max_len
        return self

    def min_items(self, min_val):
        self.schema['minItems'] = min_val
        return self

    def max_items(self, max_val):
        self.schema['maxItems'] = max_val
        return self

    def build(self):
        return self.schema.copy()

    @staticmethod
    def create():
        return SchemaBuilder()

    @staticmethod
    def array_of(item_type):
        if isinstance(item_type, str):
            return SchemaBuilder().array({'type': item_type})
        return SchemaBuilder().array(item_type)

    @staticmethod
    def object_with(properties):
        return SchemaBuilder().object(properties)
