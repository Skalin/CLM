import sys
import Fetcher


class Migrator:
    config = None

    def __init__(self, config):
        self.config = config

    def fetch_data(self):
        f = Fetcher.Fetcher(self.config)
        datatypes_lists = {}
        for i in f.get_allowed_datatypes():
            endpoint = '_'.join((i, f.list_action))
            response = f.fetch(endpoint)
            datatypes_lists[i] = response

        print(datatypes_lists)
        for i in datatypes_lists:
            print(i)
            print(datatypes_lists[i])


