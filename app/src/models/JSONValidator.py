import requests
import json
import jsonschema
from jsonschema import validate, RefResolver


class JSONValidator:
    schema = None
    api_url = ""

    def __init__(self, api_url):
        self.api_url = api_url
        self.schema = requests.get('https://ofn.gov.cz/rozhran%C3%AD-katalog%C5%AF-otev%C5%99en%C3%BDch-dat/2021-01-11/sch%C3%A9mata/datov%C3%A1-sada.json').json()

    def validate_json(self, data):
        try:
            resolver = RefResolver(referrer=self.schema, base_uri='http://')
            validate(data, self.schema, resolver=resolver)
            return True
        except RecursionError:
            return False
        except jsonschema.exceptions.ValidationError:
            return False
