import sys
import Fetcher


class Migrator:
    config = None
    endpoint = None

    def __init__(self, config, endpoint):
        self.config = config
        self.endpoint = endpoint

    def fetch_data(self, endpoint):
        f = Fetcher.Fetcher(self.config)
        response = f.fetch('_'.join((endpoint, f.list_action)))
        return response

    def migrate(self):
        pass
