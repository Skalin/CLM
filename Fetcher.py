import requests
import json

class Fetcher:
    config = None

    def __init__(self, config):
        self.config = config

    def get_storage(self):
        return None

    def get_allowed_datatypes(self):
        return ['package', 'tag', 'user']

    def get_allowed_actions(self):
        return ['show']

    def get_request(self, endpoint):
        if self.validate_endpoint(endpoint) is False:
            return {}
        headers = {
            'Authorization': 'Bearer' + self.config.access_token
        }
        r = requests.get(self.config.url+'/api/action/'+endpoint, headers = headers)
        return r.json()

    def get_packages(self):
        self.get_request('packages')

    def validate_endpoint(self, endpoint):
        datatype, action = endpoint.split('_')

        try:
            self.get_allowed_datatypes().index(datatype)
            self.get_allowed_actions().index(action)
            json_data = self.get_request(endpoint)

        except ValueError:
            return False
        return True