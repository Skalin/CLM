import json

from app.src.components.clm.JSONValidator import JSONValidator

FREQUENCY_MAP = {'R/P10Y':'DECENNIAL','R/P4Y':'QUADRENNIAL','R/P3Y':'TRIENNIAL','R/P2Y':'BIENNIAL','R/P1Y':'ANNUAL', 'R/P6M': 'ANNUAL_2','R/P4M': 'ANNUAL_3','R/P3M': 'QUARTERLY', 'R/P2M': 'BIMONTHLY', 'R/P0.5M':'BIMONTHLY','R/P1M':'MONTHLY', 'R/P0.33M': 'MONTHLY_3', 'R/P1W': 'WEEKLY',  'R/P3.5D': 'WEEKLY_2', 'R/P0.33W': 'WEEKLY_3','R/P2W':'BIWEEKLY','R/P0.5W': 'BIWEEKLY','R/P1D': 'DAILY','R/PT1H':'HOURLY','R/PT1S':'UPDATE_CONT'}



class NKODDataset:
    json_validator = None
    lkod_url = ''
    error = []

    context = 'https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld'
    typ = 'Datová sada'
    název = {'cs': ''}
    popis = {'cs': 'Nevyplněn'}
    poskytovatel = None
    téma = ["http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"],
    periodicita_aktualizace = ''
    klíčové_slovo = {'cs': ''}
    prvek_rúian = ['']
    kontaktní_bod = {}
    klíčové_slovo = {}
    distribuce = []
    koncept_euroVoc = []
    dokumentace = ''

    def __init__(self, lkod_url, vatin, dataset, form):
        self.poskytovatel = 'https://rpp-opendata.egon.gov.cz/odrpp/zdroj/orgán-veřejné-moci/' + vatin,
        self.lkod_url = lkod_url

        dataset_data = dataset.data
        if dataset_data['maintainer'] is not None and len(dataset_data['maintainer']) and len(dataset_data['maintainer_email']):
            self.kontaktní_bod = {'typ': 'Organizace', 'jméno': {'cs': dataset_data['maintainer']}, 'e-mail': 'mailto:'+dataset_data['maintainer_email']}

        if len(dataset_data['title']):
            self.název = {'cs': dataset_data['title']}

        if dataset_data['notes'] is not None and len(dataset_data['notes']):
            self.popis = {'cs': dataset_data['notes']}

        # TODO periodicita
        if 'frequency' in dataset_data and self.convert_ISO_8601_to_eu_frequency(dataset_data['frequency']) is not None:
            self.periodicita_aktualizace = self.convert_ISO_8601_to_eu_frequency(dataset_data['frequency'])

        if form is not None and form.prefill_frequency_check.data and ('periodicita_aktualizace' in self or self.periodicita_aktualizace == ''):
            self.periodicita_aktualizace = 'http://publications.europa.eu/resource/authority/frequency/'+form.prefill_frequency.data.upper()

        # TODO remove iri
        if 'spatial_uri' in dataset_data:
            self.prvek_rúian = [self.get_ruian_type(dataset_data['spatial_uri'])]
        elif 'ruian_type' in dataset_data and 'ruian_code' in dataset_data:
            self.prvek_rúian = [self.get_ruian_type(dataset_data['ruian_type'], dataset_data['ruian_code'])]
        else:
            self.prvek_rúian = ['']

        if self.prvek_rúian == [''] and form is not None and form.prefill_ruian_check.data:
            self.prvek_rúian = ['https://linked.cuzk.cz/resource/ruian/stat/1']

        self.poskytovatel = 'https://linked.opendata.cz/zdroj/ekonomický-subjekt/'+ vatin

        if 'theme' in dataset_data and len(dataset_data['theme']):
            themes = dataset_data['theme'].split()
            self.koncept_euroVoc = themes
            # TODO migrate themes into téma and properly pass euroVoc

        if 'schema' in dataset_data and len(dataset_data['schema']):
            self.dokumentace = dataset_data['schema']

        if 'extras' in dataset_data:
            extras = dataset_data['extras']
            theme = [element for element in extras if element['key'] == 'theme']
            if len(theme) > 0:
                self.téma = theme[0]['value']

        # TODO časové pokrytí
        # new_dataset['časové_pokrytí'] = {
        #    'typ': 'Časový interval',
        #    'začátek': datetime.strptime(resource['created']),
        #    'konec': datetime.strptime(resource['last_modified'])
        # }

        if 'tags' in dataset_data:
            tags = dataset_data['tags']
            new_tags = {'cs': []}
            for tag in tags:
                new_tags['cs'].append(tag['display_name'])
            self.klíčové_slovo = new_tags

        if len(dataset_data['resources']) == 0:
            return

        for resource in dataset_data['resources']:
            new_resource = {
                'iri': 'https://data.gov.cz/lkod/mdcr/datové-sady/vld/distribuce/'+self.get_final_format(resource['mimetype']),
                'typ': 'Distribuce',
                'podmínky_užití': self.get_license_prefill_prefill_value(dataset_data, resource, form),
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
            self.distribuce.append(new_resource)

    def convert_ISO_8601_to_eu_frequency(self, value):
        if value in FREQUENCY_MAP:
            return 'http://publications.europa.eu/resource/authority/frequency/'+FREQUENCY_MAP[value]
        return None

    def get_final_format(self, mimetype):
        if mimetype is None:
            return ''
        m = mimetype.split('/')
        if len(m) == 2:
            return m[1]
        return ''

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

    def get_license_prefill_prefill_value(self, dataset_data, resource, form = None):
        license_obj = {'typ': 'Specifikace podmínek užití', 'autorské_dílo': ''}
        if 'license_link' in resource:
            license_obj['autorské_dílo'] = resource['license_link']
        if len(license_obj['autorské_dílo']) == 0 and 'license_url' in dataset_data:
            license_obj['autorské_dílo'] = dataset_data['license_url']

        license_obj['databáze_jako_autorské_dílo']= dataset_data['license_url'] if 'license_url' in dataset_data else ''
        license_obj['databáze_chráněná_zvláštními_právy'] = 'https://data.gov.cz/podmínky-užití/není-chráněna-zvláštním-právem-pořizovatele-databáze/'

        if len(license_obj['autorské_dílo']) == 0 and form is not None and form.prefill_license_check.data:
            if form.prefill_license.data == 'cc4':
                license_obj['autorské_dílo'] = 'https://creativecommons.org/licenses/by/4.0'
            elif form.prefill_license.data == 'none':
                license_obj['autorské_dílo'] = 'https://data.gov.cz/podmínky-užití/neobsahuje-autorská-díla/'

        if len(license_obj['databáze_jako_autorské_dílo']) == 0 and form is not None and form.prefill_license_check.data:
            if form.prefill_license.data == 'none':
                license_obj['databáze_jako_autorské_dílo'] = 'https://data.gov.cz/podmínky-užití/není-autorskoprávně-chráněnou-databází/'

        return license_obj

    def get_ruian_prefill_value(self):
        ...

    def validate(self):
        validator = JSONValidator(self.lkod_url)
        status = validator.validate_json(self.toJson())
        self.errors = validator.errors
        return status

    def toJson(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return self.toJson()
