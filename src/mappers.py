import json
import os.path
import ast
import Fetcher
import sys
import time
import jsonschema


class Mapper:
    base_endpoint = ""
    config = None
    datatype = None

    def __init__(self, config, datatype):
        self.config = config
        self.datatype = datatype


    def set_endpoint(self, endpoint):
        self.base_endpoint = endpoint

    def get_endpoint(self):
        return self.base_endpoint


class PackageMapper(Mapper):
    data = None
    migration_dir = ""
    fetcher = None
    action = 'show'

    def set_migration_dir(self, migration_dir):
        self.migration_dir = migration_dir

    def get_migration_dir(self):
        return self.migration_dir

    def set_endpoint(self, endpoint):
        self.base_endpoint = endpoint

    def get_base_endpoint(self):
        return self.base_endpoint

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher.Fetcher(self.config)
        return self.fetcher

    def get_endpoint(self):
        return '_'.join((self.datatype, self.action))


    def process_data(self, action):
        file_name = "_".join((self.get_base_endpoint(), action))
        if os.path.exists(self.migration_dir+"/"+file_name) is False:
            return False

        with open(self.migration_dir+"/"+file_name, 'r') as reader:
            self.set_data({'old': ast.literal_eval(reader.read())})

        storage_dir = '/'.join((self.get_migration_dir(), self.get_endpoint()))
        if os.path.exists(storage_dir) is False:
            os.mkdir(storage_dir)

        fetcher = self.get_fetcher()
        for item in self.get_data()['old']:
            print("Fetching \""+item+"\" in datatype \""+self.datatype+"\".")
            fetch_item = fetcher.fetch(self.get_endpoint(), {'id': item})
            print("Fetched \""+item+"\" successfully.")
            f = self.init_file('/'.join((self.get_migration_dir(), self.get_endpoint(), item+".json")))
            f.write(json.dumps(fetch_item))
            f.close()
        print("All files were successfully downloaded. Started parsing …")
        self.parse_data()

    def parse_data(self):
        for item in self.get_data()['old']:
            print("Parsing \""+item+"\" in datatype \""+self.datatype+"\".")
            json_old = None
            with open('/'.join((self.get_migration_dir(), self.get_endpoint(), item+".json")), 'r') as reader:
                json_old = json.loads(reader.read())

            if json_old is None:
                return False

            for attr in json_old:
                print(attr+": "+repr(json_old[attr]))
            sys.exit(1)

            # validate new json according to NKOD structure
            #self.validate_json(new_structure)
            # save to new file with name old_json_new
            f = self.init_file('/'.join((self.get_migration_dir(), self.get_endpoint(), item+"_new.json")))
            f.close()

            print("Saved item successfully \""+item+"\" successfully.")
        print("All files were successfully parsed into new files. Started validating …")
        ...

    def validate_json(self, json):
        ...

    def init_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w")
        return f

    def write_output(self, string):
        sys.stdout.write(string+"\r")
        sys.stdout.flush()
        time.sleep(1)