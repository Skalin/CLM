import json
import sys

import requests
from flask import session
from app.src.components.clm.Config import Config
from app.src.components.clm.Fetcher import Fetcher
from app.src.models.JSONValidator import JSONValidator

CONSTANT_JSON_VALID = 'valid'
CONSTANT_JSON_INVALID = 'invalid'


FREQUENCY_MAP = {'R/P10Y':'DECENNIAL','R/P4Y':'QUADRENNIAL','R/P3Y':'TRIENNIAL','R/P2Y':'BIENNIAL','R/P1Y':'ANNUAL', 'R/P6M': 'ANNUAL_2','R/P4M': 'ANNUAL_3','R/P3M': 'QUARTERLY', 'R/P2M': 'BIMONTHLY', 'R/P0.5M':'BIMONTHLY','R/P1M':'MONTHLY', 'R/P0.33M': 'MONTHLY_3', 'R/P1W': 'WEEKLY',  'R/P3.5D': 'WEEKLY_2', 'R/P0.33W': 'WEEKLY_3','R/P2W':'BIWEEKLY','R/P0.5W': 'BIWEEKLY','R/P1D': 'DAILY','R/PT1H':'HOURLY','R/PT1S':'UPDATE_CONT'}

class Migrator:
    dataset_endpoints = []
    fetcher = None
    config = None
    migration_type = None
    vatin = ''
    datasets = {}

    def __init__(self, lkod_url, ckan_url, access_token, vatin, migration_type=None, datasets={'valid': [], 'invalid': []}):
        self.config = Config(ckan_url, access_token)
        self.vatin = vatin
        self.migration_type = migration_type
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
            except requests.ConnectionError:
                print("Connection error")
                return False
            return True

    def prepare_datasets(self):
        self.fetch_datasets()
        for dataset in self.dataset_endpoints:
            self.validate_dataset(dataset=dataset)
        return self.datasets

    def get_new_dataset(self, dataset):
        return json.dumps(self.get_new_dataset_object(dataset))

    def get_new_dataset_object(self, dataset, form=None):
        old = self.fetch_old_dataset(dataset)
        return self.prepare_dataset_json_object(old, form)

    def prepare_dataset_json_object(self, dataset, form=None, prefill_ruian=False):
        if not dataset:
            return {}
        new_dataset = {
            '@context': 'https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld',
            'iri': 'https://data.gov.cz/lkod/mdcr/datové-sady/vld',
            'typ': 'Datová sada',
            'název': {'cs': ''},
            'popis': {'cs': 'Nevyplněn'},
            'poskytovatel': 'https://rpp-opendata.egon.gov.cz/odrpp/zdroj/orgán-veřejné-moci/' + self.vatin,
            'téma': ["http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"],
            'periodicita_aktualizace': '',
            'klíčové_slovo': {'cs': []},
            'prvek_rúian': [''],
        }

        if dataset['maintainer'] is not None and len(dataset['maintainer']) and len(dataset['maintainer_email']):
            new_dataset['kontaktní_bod'] = {'typ': 'Organizace', 'jméno': {'cs': dataset['maintainer']}, 'e-mail': 'mailto:'+dataset['maintainer_email']}

        if len(dataset['title']):
            new_dataset['název'] = {'cs': dataset['title']}

        if dataset['notes'] is not None and len(dataset['notes']):
            new_dataset['popis'] = {'cs': dataset['notes']}

        if 'frequency' in dataset and self.convert_ISO_8601_to_eu_frequency(dataset['frequency']) is not None:
            new_dataset['periodicita_aktualizace'] = self.convert_ISO_8601_to_eu_frequency(dataset['frequency'])

        if form is not None and form.prefill_frequency_check.data and ('periodicita_aktualizace' in new_dataset or new_dataset['periodicita_aktualizace'] == ''):
            new_dataset['periodicita_aktualizace'] = 'http://publications.europa.eu/resource/authority/frequency/'+form.prefill_frequency.data.upper()


        if 'spatial_uri' in dataset:
            new_dataset['prvek_rúian'] = [self.get_ruian_type(dataset['spatial_uri'])]
        elif 'ruian_type' in dataset and 'ruian_code' in dataset:
            new_dataset['prvek_rúian'] = [self.get_ruian_type(dataset['ruian_type'], dataset['ruian_code'])]
        else:
            new_dataset['prvek_rúian'] = ['']

        if new_dataset['prvek_rúian'] == [''] and form is not None and form.prefill_ruian_check.data:
            new_dataset['prvek_rúian'] = ['https://linked.cuzk.cz/resource/ruian/stat/1']

        new_dataset['poskytovatel'] = 'https://linked.opendata.cz/zdroj/ekonomický-subjekt/'+ self.vatin

        if 'theme' in dataset and len(dataset['theme']):
            themes = dataset['theme'].split()
            new_dataset['koncept_euroVoc'] = themes

        if 'schema' in dataset and len(dataset['schema']):
            new_dataset['dokumentace'] = dataset['schema']

        if 'extras' in dataset:
            extras = dataset['extras']
            theme = [element for element in extras if element['key'] == 'theme']
            if len(theme) > 0:
                new_dataset['téma'] = theme[0]['value']
        if 'tags' in dataset:
            tags = dataset['tags']
            new_tags = {'cs': []}
            for tag in tags:
                new_tags['cs'].append(tag['display_name'])
            new_dataset['klíčové_slovo'] = new_tags

        if len(dataset['resources']) == 0:
            return new_dataset
        new_dataset['distribuce'] = []
        # new_dataset['časové_pokrytí'] = {
        #    'typ': 'Časový interval',
        #    'začátek': datetime.strptime(resource['created']),
        #    'konec': datetime.strptime(resource['last_modified'])
        # }

        for resource in dataset['resources']:
            new_resource = {
                'iri': 'https://data.gov.cz/lkod/mdcr/datové-sady/vld/distribuce/'+self.get_final_format(resource['mimetype']),
                'typ': 'Distribuce',
                'podmínky_užití': {
                    'typ': 'Specifikace podmínek užití',
                    'autorské_dílo': resource['license_link'] if 'license_link' in resource else dataset['license_url'] if 'license_url' in dataset else '',
                    'databáze_jako_autorské_dílo': dataset['license_url'] if 'license_url' in dataset else '',
                    'databáze_chráněná_zvláštními_právy': 'https://data.gov.cz/podmínky-užití/není-chráněna-zvláštním-právem-pořizovatele-databáze/',
                    'osobní_údaje': 'https://data.gov.cz/podmínky-užití/neobsahuje-osobní-údaje/',
                },
                'název': {
                    'cs': resource['name']
                },
                'soubor_ke_stažení': resource['url'],
                'přístupové_url': resource['url'],
                'formát': 'http://publications.europa.eu/resource/authority/file-type/' + resource['format']
            }
            if 'mimetype' in resource and resource['mimetype'] is not None:
                new_resource['typ_média'] = 'http://www.iana.org/assignments/media-types/' + resource[
                    'mimetype']
            new_dataset['distribuce'].append(new_resource)

        return new_dataset

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

    def get_final_format(self, mimetype):
        if mimetype is None:
            return ''
        m = mimetype.split('/')
        if len(m) == 2:
            return m[1]
        return ''

    def convert_ISO_8601_to_eu_frequency(self, value):
        if value in FREQUENCY_MAP:
            return 'http://publications.europa.eu/resource/authority/frequency/'+FREQUENCY_MAP[value]
        return None

    def get_ruian_type(self, uri = None, ruian_type = None, ruian_code = None):
        if uri is not None:
            uri_params = uri.split('/')[-2:]
            if len(uri_params) == 2:
                return 'https://linked.cuzk.cz/resource/ruian/'+uri_params[0]+'/'+uri_params[1]
            else:
                return ''

        if ruian_type is not None:
            return_value = ''
            if ruian_type == 'ST':
                return_value = 'stat'
            elif ruian_type == 'MČ':
                return_value = 'mestskecasti'
            elif ruian_type == 'OB':
                return_value = 'obec'
            elif ruian_type == 'OK':
                return_value = 'okres'
            else:
                return_value = 'stat'
            if ruian_code is None:
                return ''
            return 'https://linked.cuzk.cz/resource/ruian/'+return_value+'/'+ruian_code
        return ''

    def get_frequency_prefill_value(self):
        ...

    def get_license_prefill_prefill_value(self):
        ...

    def get_ruian_prefill_value(self):
        ...