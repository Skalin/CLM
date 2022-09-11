import json
import sys

from app.src.models.NKODDataset import NKODDataset, CONSTANT_JSON_VALID, CONSTANT_JSON_INVALID

import requests
from flask import session
from app.src.components.clm.Config import Config
from app.src.components.clm.Fetcher import Fetcher
from app.src.models.JSONValidator import JSONValidator

class Migrator:
    lkod_url = ''
    dataset_endpoints = []
    fetcher = None
    config = None
    migration_type = None
    vatin = ''
    datasets = {}

    def __init__(self, lkod_url, ckan_url, access_token, vatin, migration_type=None, datasets=None):
        if datasets is None:
            datasets = {CONSTANT_JSON_VALID: [], CONSTANT_JSON_INVALID: []}

        self.config = Config(ckan_url, access_token)
        self.vatin = vatin
        self.migration_type = migration_type
        self.lkod_url = lkod_url
        self.json_validator = JSONValidator(lkod_url)
        self.license_prefill = None
        self.frequency_prefill = None
        self.ruian_prefill = ['']
        self.datasets = datasets

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher(self.config)
        return self.fetcher

    def fetch_datasets(self):
        self.dataset_endpoints = []
        response = self.get_fetcher().get_request(
            'package_search?include_private=' + ('true' if len(self.config.access_token) else 'false') + '&rows=1000')
        if not response:
            return response
        for dataset in response['results']:
            self.dataset_endpoints.append(dataset['name'])
        return self.dataset_endpoints

    def migrate(self, form):
        if type(self.datasets) is str:
            self.datasets = eval(self.datasets)
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            if self.migration_type == 'all':
                self.migrate_dataset(dataset, form)
            elif self.migration_type == 'valid' and dataset in self.datasets[self.migration_type]:
                self.migrate_dataset(dataset, form)
            elif self.migration_type == 'invalid' and dataset in self.datasets[self.migration_type]:
                self.migrate_dataset(dataset, form)

    def migrate_dataset(self, dataset, form=None):
        dataset = self.get_new_dataset_object(dataset, form)
        if 'lkod' not in session:
            return False
        lkod = session['lkod']
        response = requests.post(lkod['url'] + '/datasets', data={'organizationId': lkod['organization']},
                                 headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
        if 'id' in response:
            dataset_id = response['id']
            session_response = requests.post(lkod['url'] + '/sessions', data={'datasetId': dataset_id},
                                             headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
            session_id = session_response['id']
            user_data = {'accessToken': lkod['accessToken'], 'sessionId': session_id, 'datasetId': dataset_id}
            print(json.dumps(dataset))
            try:
                form_response = requests.post(lkod['url'] + '/form-data',
                                          headers={'ContentType': 'application/x-www-form-urlencoded'},
                                          json={'userData': json.dumps(user_data), 'formData': json.dumps(dataset)},)
                print(form_response.url)
                self.migrate_resources_for_dataset(lkod['url'], dataset, dataset_id)
            except requests.ConnectionError:
                print("Connection error")
                return False
            return True

    def migrate_resources_for_dataset(self, lkod_url, dataset, dataset_id):
        for resource in dataset.distribuce:
            file = requests.get(resource.soubor_ke_stažení, stream=True)
            requests.post(lkod_url+'/datasets/'+dataset_id+'/files', headers={'ContentType': 'multipart/form-data'}, json={'datasetFile':file})

    def prepare_datasets(self, form=None):
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            dataset_model = NKODDataset(self.lkod_url, self.vatin, dataset, form)
            dataset_model.validate()
        return self.datasets

    def get_new_dataset(self, dataset):
        return json.dumps(self.get_new_dataset_object(dataset))

    def get_new_dataset_object(self, dataset, form=None):
        old = self.fetch_old_dataset(dataset)
        return self.prepare_dataset_json_object(old, form)

    def prepare_dataset_json_object(self, dataset, form=None):
        if not dataset:
            return {}
        # TODO remove iri
        dataset_model = NKODDataset(self.vatin, self.json_validator, dataset, form)
        return dataset_model

    def fetch_old_dataset(self, dataset):
        return self.get_fetcher().fetch('package_show', {'id': dataset})

    def validate_dataset(self, dataset):
        valid_state = self.json_validator.validate_json(self.get_new_dataset_object(dataset), dataset)
        self.push_to_array(dataset, valid_state)

    def push_to_array(self, dataset, status):
        if status is True:
            self.datasets[CONSTANT_JSON_VALID].append(dataset)
        elif status is False:
            self.datasets[CONSTANT_JSON_INVALID].append(dataset)

    def prepare_dataset_json(self, dataset, prefill_empty=False):
        print('preparing next dataset')

        new_dataset = self.prepare_dataset_json_object(dataset, prefill_empty)
        return json.dumps(new_dataset)
