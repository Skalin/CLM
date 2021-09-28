import requests
import json


class Fetcher:
    config = None
    list_action = 'list'
    actions = ['list', 'show']
    datatypes = ['package', 'tag', 'user']

    def __init__(self, config, actions=None, datatypes=None):
        self.config = config
        if actions is not None:
            self.actions = actions
        if datatypes is not None:
            self.datatypes = datatypes

    def get_storage(self):
        return None

    def get_allowed_datatypes(self):
        return self.datatypes

    def get_allowed_actions(self):
        return self.actions

    def get_request(self, endpoint):
        if self.validate_endpoint(endpoint) is False:
            return {}
        headers = {
            'Authorization': self.config.access_token
        }
        r = requests.get('/'.join((self.config.base_url, 'api/action', endpoint)))
        data = r.json()
        if data.get('success') is not True:
            return []
        return data.get('result')

    def fetch(self, endpoint):
        return self.get_request(endpoint)

    def validate_endpoint(self, endpoint):
        datatype, action = endpoint.split('_')

        if self.get_allowed_datatypes().index(datatype) is ValueError:
            return False
        if self.get_allowed_actions().index(action) is ValueError:
            return False
        return True
