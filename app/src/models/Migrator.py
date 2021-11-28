import json
import requests
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

    def __init__(self, lkod_url, ckan_url, access_token, vatin, migration_type=None):
        self.config = Config(ckan_url, access_token)
        self.vatin = vatin
        self.migration_type = migration_type
        self.json_validator = JSONValidator(lkod_url)
        self.datasets = {'valid': [], 'invalid': []}

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher(self.config)
        return self.fetcher

    def fetch_datasets(self):
        self.dataset_endpoints = []
        response = self.get_fetcher().get_request('package_search?include_private='+('true' if len(self.config.access_token) else 'false')+'&rows=1000')
        if not response:
            return response
        for dataset in response['results']:
            self.dataset_endpoints.append(dataset['name'])
        return self.dataset_endpoints

    def migrate(self):
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            self.validate_dataset(dataset=dataset)
        return len(self.datasets[CONSTANT_JSON_INVALID]) == 0

    def prepare_datasets(self):
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            self.validate_dataset(dataset=dataset)
        return self.datasets

    def get_new_dataset(self, dataset):
        return json.dumps(self.get_new_dataset_object(dataset))

    def get_new_dataset_object(self, dataset):
        old = self.fetch_old_dataset(dataset)
        return self.prepare_dataset_json_object(old)

    def prepare_dataset_json_object(self, dataset, prefill_empty = False):
        if not dataset:
            return {}
        new_dataset = {
            '@context': 'https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld',
            'iri': 'https://data.gov.cz/lkod/mdcr/datové-sady/vld',
            'typ': 'Datová sada',
            'název': {'cs': dataset['title']},
            'popis': {'cs': dataset['notes']},
            'poskytovatel': 'https://rpp-opendata.egon.gov.cz/odrpp/zdroj/orgán-veřejné-moci/'+self.vatin
        }

        if 0 not in dataset['resources']:
            if prefill_empty:
                new_dataset['prvek_rúian'] = []
                new_dataset['geografické_území'] = []
                new_dataset['prostorové_pokrytí'] = []
                new_dataset['klíčové_slovo'] = {'cs': [], 'en': []}
                new_dataset[
                    'periodicita_aktualizace'] = "http://publications.europa.eu/resource/authority/frequency/MONTHLY"
                new_dataset['distribuce'] = []
                new_dataset['geografické_území'] = []
            return new_dataset
        resource = dataset['resources'][0]
        print(resource)
        new_dataset['dokumentace'] = 'https://operator-ict.gitlab.io/golemio/documentation'
        if 'spatial_uri' in dataset:
            new_dataset['prvek_rúian'] = dataset['spatial_uri']
        new_dataset['poskytovatel'] = '/'.join(('https://linked.opendata.cz/zdroj/ekonomický-subjekt/', self.vatin))
        new_dataset['periodicita_aktualizace'] = 'http://publications.europa.eu/resource/authority/frequency/MONTHLY'

        # new_dataset['časové_pokrytí'] = {
        #    'typ': 'Časový interval',
        #    'začátek': datetime.strptime(resource['created']),
        #    'konec': datetime.strptime(resource['last_modified'])
        # }

        new_dataset['distribuce'] = [{
            'typ': 'Distribuce',
            'název': {
                'cs': resource['name']
            },
            'soubor_ke_stažení': resource['url'],
            'přístupové_url': resource['url'],
            'formát': 'http://publications.europa.eu/resource/authority/file-type/' + resource['format']
        }]

        if 'mimetype' in resource and resource['mimetype'] is not None:
            new_dataset['distribuce'][0]['typ_média'] = 'http://www.iana.org/assignments/media-types/' + resource[
                'mimetype']
        if 'extras' in dataset:
            extras = dataset['extras']
            theme = [element for element in extras if element['key'] == 'theme']
            if len(theme) > 0:
                new_dataset['téma'] = theme[0]['value']
        if 'tags' in dataset:
            tags = dataset['tags']
            new_dataset['klíčové_slovo'] = tags
        return dataset

    def fetch_old_dataset(self, dataset):
        return self.get_fetcher().fetch('package_show', {'id': dataset})

    def validate_dataset(self, dataset):
        valid_state = self.json_validator.validate_json(self.get_new_dataset(dataset), dataset)
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
