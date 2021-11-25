import requests
import json
from flask import session


class LKODUser:
    url = None
    access_token = None

    def __init__(self, url):
        self.url = url

    def login(self, username, password):
        data = requests.post(self.url+'/login', data={'email': username, 'password': password})
        content = json.loads(data.content)
        if 'accessToken' not in content:
            session['lkod'] = None
            print("return false")
            return False

        self.access_token = content['accessToken']
        session['lkod'] = {'url': self.url, 'accessToken': self.access_token}
        return True
