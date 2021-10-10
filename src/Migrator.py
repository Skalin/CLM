import sys
import Fetcher
import os
import datetime
import mappers
import json


class Migrator:
    migration_dir_prefix = "migration_data"
    config = None
    fetcher = None

    def __init__(self, config):
        self.config = config
        self.get_fetcher()

    def fetch_data(self, endpoint):
        response = self.get_fetcher().fetch('_'.join((endpoint, self.get_fetcher().list_action)))
        return response

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher.Fetcher(self.config)
        return self.fetcher

    def migrate(self):
        migration_dir = self.migration_dir_prefix+"_"+datetime.datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(migration_dir) is False:
            os.mkdir(migration_dir)

        for datatype in self.get_fetcher().datatypes:
            # maybe write handler for unfinished migrations..
            f = self.init_file(migration_dir+"/"+datatype+"_"+self.fetcher.list_action)
            f.write(json.dumps(self.get_fetcher().get_request('_'.join((datatype, self.get_fetcher().list_action)))))
            mapper = getattr(mappers, self.fetcher.datatypes[datatype]['class'])()
            mapper.process_data('list')


    def init_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w")
        return f



