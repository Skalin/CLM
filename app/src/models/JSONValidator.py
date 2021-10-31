import requests
import json
import jsonschema
from jsonschema import Draft7Validator
import jsonref


class JSONValidator:
    schema = None
    resolver = None
    api_url = ""
    errors = {}

    def __init__(self, api_url):
        self.api_url = api_url
        self.schema = requests.get('https://ofn.gov.cz/rozhran%C3%AD-katalog%C5%AF-otev%C5%99en%C3%BDch-dat/2021-01-11/sch%C3%A9mata/datov%C3%A1-sada.json').json()

    def validate_json(self, data, dataset):
        try:
            validator = Draft7Validator(self.schema)
            validator.validate(data)
            return True
        except RecursionError as e:
            self.errors[dataset] = e
            return False
        except jsonschema.exceptions.ValidationError as e:
            self.errors[dataset] = e
            return False
