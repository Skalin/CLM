import json
import os.path
import ast
import Fetcher
import sys
import time


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

    def process_data(self, migration_dir, action):
        file_name = "_".join((self.endpoint, action))
        if os.path.exists(self.migration_dir+"/"+file_name) is False:
            return False

        with open(self.migration_dir+"/"+file_name, 'r') as reader:
            data = ast.literal_eval(reader.read())

        current_action = 'show'
        datatype = 'package'
        endpoint = '_'.join((datatype, current_action))
        storage_dir = migration_dir+"/"+endpoint
        if os.path.exists(storage_dir) is False:
            os.mkdir(storage_dir)

        fetcher = self.get_fetcher()
        for item in data:
            self.write_output("Fetching \""+item+"\" in datatype \""+datatype+"\".")
            fetch_item = fetcher.fetch(endpoint, {'id': item})
            self.write_output("Fetched \""+item+"\" successfully.")
            f = self.init_file(migration_dir+"/"+endpoint+"/"+item)
            f.write(json.dumps(fetch_item))
            f.close()
        print("All files were successfully downloaded. Prepare parsing");
        self.parse_data()

    def parse_data(self):
        pass

    def init_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w")
        return f

    def write_output(self, string):
        sys.stdout.write(string+"\r")
        sys.stdout.flush()
        time.sleep(1)