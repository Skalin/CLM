import requests
import json


class LKODUser:
    url = None
    access_token = None

    def __init__(self, url):
        self.url = url

    def login(self, username, password):
        data = requests.post(self.url+'/login', data={'email': username, 'password': password})
        content = json.loads(data.content)
        print(content)
        if 'accessToken' in content:
            self.access_token = content['accessToken']
            return True
        return False
