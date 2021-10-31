import json

class Config:
    access_token = None
    encoding = 'utf-8'
    base_url = None

    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.access_token = access_token

    def set_mapper(self, mapping_json):
        self.mapper = json.loads(mapping_json)

    def get_mapper(self):
        return self.mapper

    def get_new_mapping_name(self, old_mapping_name):
        if (self.mapper[old_mapping_name]) is not None:
            return self.mapper[old_mapping_name]
