import sys
import requests
from datetime import datetime
from app.src.components.clm.Config import Config
from app.src.components.clm.Fetcher import Fetcher
from app.src.models.JSONValidator import JSONValidator

CONSTANT_JSON_VALID = 'valid'
CONSTANT_JSON_INVALID = 'invalid'


class Migrator:
    dataset_endpoints = []
    fetcher = None
    config = None
    migration_type = None
    vatin = ''
    datasets = {}

    def __init__(self, lkod_url, ckan_url, access_token, vatin, migration_type):
        self.config = Config(ckan_url, access_token)
        self.vatin = vatin
        self.migration_type = migration_type
        self.json_validator = JSONValidator(lkod_url)
        self.datasets = {'valid': [], 'invalid': []}

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher(self.config)
        return self.fetcher

    def migrate(self):
        self.dataset_endpoints = self.get_fetcher().get_request('_'.join(('package', self.get_fetcher().list_action)))
        for dataset in self.dataset_endpoints:
            data = self.fetcher.fetch('package_show', {'id': dataset})
            self.migrate_dataset(dataset, data)
        return self.datasets

    def migrate_dataset(self, dataset, data):
        new_data = self.prepare_dataset_json(data)
        valid_state = self.json_validator.validate_json(new_data)
        if (self.migration_type == 'all' or self.migration_type == CONSTANT_JSON_VALID) and valid_state is True:
            self.datasets[CONSTANT_JSON_VALID].append(dataset)
        elif (self.migration_type == 'all' or self.migration_type == CONSTANT_JSON_INVALID) and valid_state is False:
            self.datasets[CONSTANT_JSON_INVALID].append(dataset)

    def prepare_dataset_json(self, data):
        new_data = {
            '@context': 'https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld',
            'iri': 'https://data.gov.cz/lkod/mdcr/datové-sady/vld', 'typ': 'Datová sada',
            'název': {'cs': data['title']}}
        resource = data['resources'][0]
        new_data['popis'] = {'cs': resource['name']}
        new_data['dokumentace'] = 'https://operator-ict.gitlab.io/golemio/documentation'
        new_data['prvek_rúian'] = 'https://linked.cuzk.cz/resource/ruian/stat/1'
        new_data['poskytovatel'] = '/'.join(('https://linked.opendata.cz/zdroj/ekonomický-subjekt/', self.vatin))
        new_data['periodicita_aktualizace'] = 'http://publications.europa.eu/resource/authority/frequency/MONTHLY'

        # new_data['časové_pokrytí'] = {
        #    'typ': 'Časový interval',
        #    'začátek': datetime.strptime(resource['created']),
        #    'konec': datetime.strptime(resource['last_modified'])
        # }
        new_data['distribuce'] = [{
            'typ_média': 'http://www.iana.org/assignments/media-types/' + resource['mimetype'],
            'typ': 'Distribuce',
            'název': {
                'cs': resource['name']
            },
            'soubor_ke_stažení': resource['url'],
            'přístupové_url': resource['url'],
            'formát': 'http://publications.europa.eu/resource/authority/file-type/' + resource['format']
        }]
        return new_data
