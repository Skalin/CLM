import requests
import json
from flask import session


class LKODUser:
    url = None
    access_token = None
    organization_id = None

    def __init__(self, url):
        self.url = url

    def login(self, username, password):
        data = requests.post(self.url+'/login', data={'email': username, 'password': password})
        content = json.loads(data.content)
        if 'accessToken' not in content:
            session['lkod'] = None
            return False

        self.access_token = content['accessToken']
        session['lkod'] = {'url': self.url, 'accessToken': self.access_token}
        return True

    def get_organization(self, vatin):
        data = requests.get(self.url+'/organizations', headers={'Authorization': 'Bearer ' + self.access_token}).json()
        content = data
        for organization in content:
            if vatin == organization['identificationNumber']:
                session['lkod']['organization'] = organization['id']
                self.organization_id = organization['id']
                return True
        return False
