import requests
import json


class Fetcher:
    mapper_class = 'Mapper'
    config = None
    list_action = 'list'
    actions = ['list', 'show']
    datatypes = {
                    'package': {'class': 'PackageMapper'},
                    #'tag', 'user', 'member', 'organization', 'license'
    }

    def __init__(self, config, actions=None, datatypes=None):
        self.config = config
        if actions is not None:
            self.actions = actions
        if datatypes is not None:
            self.datatypes = datatypes

    def get_storage(self):
        return None

    def get_allowed_datatypes(self):
        return self.datatypes.keys()

    def get_allowed_actions(self):
        return self.actions

    def get_request(self, endpoint):
        if self.validate_endpoint(endpoint) is False:
            return {}
        headers = {
            'Authorization': self.config.access_token
        }
        print(headers)
        route = '/'.join((self.config.base_url, 'api/action', endpoint))
        print(route)
        r = requests.get(route, headers=headers)
        data = r.json()
        print(data)
        if data.get('success') is not True:
            return []
        return data.get('result')

    def fetch(self, endpoint):
        return self.get_request(endpoint)

    def validate_endpoint(self, endpoint):
        datatype, action = endpoint.split('_')

        if datatype in self.get_allowed_datatypes():
            return False
        if self.get_allowed_actions().count(action) == 0:
            return False
        return True
