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
        self.dataset_endpoints = self.get_fetcher().get_request('_'.join(('package', self.get_fetcher().list_action)))
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
        old = self.fetch_old_dataset(dataset)
        return self.prepare_dataset_json(old)

    def fetch_old_dataset(self, dataset):
        return self.get_fetcher().fetch('package_show', {'id': dataset})

    def validate_dataset(self, dataset):
        valid_state = self.json_validator.validate_json(self.get_new_dataset(dataset), dataset)
        if valid_state is True:
            self.datasets[CONSTANT_JSON_VALID].append(dataset)
        elif valid_state is False:
            self.datasets[CONSTANT_JSON_INVALID].append(dataset)

    def create_dataset(self, organizationId):
        requests.post()

    def prepare_dataset_json(self, data, prefill_empty=False):
        print('preparing next dataset')

        if not data:
            return json.dumps({})
        new_data = {
            '@context': 'https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld',
            'iri': 'https://data.gov.cz/lkod/mdcr/datové-sady/vld',
            'typ': 'Datová sada',
            'název': {'cs': data['title']}}
        if 0 not in data['resources']:
            if prefill_empty:
                new_data['popis'] = []
                new_data['prvek_rúian'] = []
                new_data['geografické_území'] = []
                new_data['prostorové_pokrytí'] = []
                new_data['klíčové_slovo'] = {'cs': [], 'en': []}
                new_data[
                    'periodicita_aktualizace'] = "http://publications.europa.eu/resource/authority/frequency/MONTHLY"
                new_data['poskytovatel'] = ''
                new_data['distribuce'] = []
                new_data['geografické_území'] = []
            return json.dumps(new_data)
        resource = data['resources'][0]
        print(resource)
        new_data['popis'] = {'cs': resource['name']}
        new_data['dokumentace'] = 'https://operator-ict.gitlab.io/golemio/documentation'
        if 'spatial_uri' in data:
            new_data['prvek_rúian'] = data['spatial_uri']
        new_data['poskytovatel'] = '/'.join(('https://linked.opendata.cz/zdroj/ekonomický-subjekt/', self.vatin))
        new_data['periodicita_aktualizace'] = 'http://publications.europa.eu/resource/authority/frequency/MONTHLY'

        # new_data['časové_pokrytí'] = {
        #    'typ': 'Časový interval',
        #    'začátek': datetime.strptime(resource['created']),
        #    'konec': datetime.strptime(resource['last_modified'])
        # }

        new_data['distribuce'] = [{
            'typ': 'Distribuce',
            'název': {
                'cs': resource['name']
            },
            'soubor_ke_stažení': resource['url'],
            'přístupové_url': resource['url'],
            'formát': 'http://publications.europa.eu/resource/authority/file-type/' + resource['format']
        }]

        if 'mimetype' in resource and resource['mimetype'] is not None:
            new_data['distribuce'][0]['typ_média'] = 'http://www.iana.org/assignments/media-types/' + resource[
                'mimetype']
        if 'extras' in data:
            extras = data['extras']
            theme = [element for element in extras if element['key'] == 'theme']
            if len(theme) > 0:
                new_data['téma'] = theme[0]['value']
        if 'tags' in data:
            tags = data['tags']
            new_data['klíčové_slovo'] = tags

        return json.dumps(new_data)
