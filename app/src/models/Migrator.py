import json
from app.src.models.CKANDataset import CKANDataset

from app.src.models.NKODDataset import NKODDataset
from app.src.components.clm.MigrationVariant import MigrationVariant

import requests
from flask import session
from app.src.components.clm.Config import Config
from app.src.components.clm.Fetcher import Fetcher
from app.src.components.clm.JSONValidator import JSONValidator
from app.src.components.clm.MigrationVariant import MigrationVariant

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
            datasets = {MigrationVariant.VALID.value: [], MigrationVariant.INVALID.value: []}

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
        return

    def migrate(self, form):
        if type(self.datasets) is str:
            self.datasets = eval(self.datasets)
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            if (self.migration_type == MigrationVariant.ALL.value) or (self.migration_type != MigrationVariant.ALL.value and dataset in self.datasets[self.migration_type]):
                self.migrate_dataset(dataset, form)

    def migrate_dataset(self, dataset, form=None):
        dataset = self.get_transformed_dataset(dataset, form)

        if 'migrator' not in session and 'lkod' not in session['migrator']:
            return False
        lkod = session['migrator']['lkod']
        response = requests.post(lkod['url'] + '/datasets', data={'organizationId': lkod['organizationId']},
                                 headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
        if 'id' in response:
            dataset_id = response['id']
            session_response = requests.post(lkod['url'] + '/sessions', data={'datasetId': dataset_id},
                                             headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
            session_id = session_response['id']
            user_data = {'accessToken': lkod['accessToken'], 'sessionId': session_id, 'datasetId': dataset_id}
            try:
                form_response = requests.post(lkod['url'] + '/form-data',
                                          headers={'ContentType': 'application/x-www-form-urlencoded'},
                                          json={'userData': json.dumps(user_data), 'formData': dataset.toJson()},)
                print(form_response.content)
                self.migrate_resources_for_dataset(lkod['url'], dataset, dataset_id)
            except requests.ConnectionError:
                return False
            return True

    def migrate_resources_for_dataset(self, lkod_url, dataset, dataset_id):
        for resource in dataset.distribuce:
            file = requests.get(resource["soubor_ke_stažení"])
            requests.post(lkod_url+'/datasets/'+dataset_id+'/files', headers={'ContentType': 'multipart/form-data'}, files={'datasetFile':file.content})

    def prepare_datasets(self, form=None):
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            dataset_model = NKODDataset(self.lkod_url, self.vatin, self.fetch_old_dataset(dataset), form)
            self.push_to_array(dataset, dataset_model.validate())
        return self.datasets

    def get_transformed_dataset(self, dataset, form=None):
        old = self.fetch_old_dataset(dataset)
        return self.transform_dataset(old, form)

    def transform_dataset(self, ckan_dataset, form=None):
        if not ckan_dataset:
            return {}
        dataset_model = NKODDataset(self.lkod_url, self.vatin, ckan_dataset, form)
        return dataset_model

    def fetch_old_dataset(self, dataset):
        ckan_dataset = CKANDataset(self.get_fetcher(), dataset)
        return ckan_dataset

    def push_to_array(self, dataset, status):
        if status is True:
            self.datasets[MigrationVariant.VALID.value].append(dataset)
        elif status is False:
            self.datasets[MigrationVariant.INVALID.value].append(dataset)