import json
import os.path
import ast
import Fetcher


class Mapper:
    pass

class PackageMapper(Mapper):
    data = None
    endpoint = ""
    migration_dir = ""
    config = None
    fetcher = None

    def __init__(self, config):
        self.config = config

    def set_migration_dir(self, migration_dir):
        self.migration_dir = migration_dir

    def get_migration_dir(self):
        return self.migration_dir

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint

    def get_endpoint(self):
        return self.endpoint

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher.Fetcher(self.config)
        return self.fetcher

    def process_data(self, action):
        file_name = "_".join((self.endpoint, action))
        if os.path.exists(self.migration_dir+"/"+file_name) is False:
            return False

        with open(self.migration_dir+"/"+file_name, 'r') as reader:
            data = ast.literal_eval(reader.read())

        fetcher = self.get_fetcher()
        for item in data:
            print(fetcher.fetch('package_show', {'id': item}))


