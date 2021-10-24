import jsonschema.exceptions
import requests
import json
from jsonschema import validate


class JSONValidator:

    schema_url = ''
    _json_schema = None

    def __init__(self, schema_url):
        self.schema_url = schema_url

    def get_json_schema(self):
        if self._json_schema is None:
            self._json_schema = self.fetch_json_schema()
        return self._json_schema

    def fetch_json_schema(self):
        return requests.get(self.schema_url)

    def validate(self, json):
        try:
            validate(json, self.get_json_schema())
        except jsonschema.exceptions.ValidationError as err:
            print(err.message)
            return False
        return True

