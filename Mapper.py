import json

# This should build my own custom object with my data so I do not have to walk through whole config every time I access it.
class Mapper:
    encoding = 'utf-8'
    mapper = ''

    def __init__(self, encoding):
        self.encoding = encoding


    def set_mapper(self, mapping_json):
        self.mapper = json.loads(mapping_json)

    def get_mapper(self):
        return self.mapper

    def get_new_mapping_name(self, old_mapping_name):
        if (self.mapper[old_mapping_name]) is not None:
            return self.mapper[old_mapping_name]



