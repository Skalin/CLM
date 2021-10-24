import json
import os.path
import ast
import Fetcher
import sys
import time


class Mapper:
    base_endpoint = ""
    config = None
    datatype = None

    def __init__(self, config, datatype):
        self.config = config
        self.datatype = datatype


    def set_endpoint(self, endpoint):
        self.base_endpoint = endpoint

    def get_endpoint(self):
        return self.base_endpoint


class PackageMapper(Mapper):
    data = None
    migration_dir = ""
    fetcher = None
    action = 'show'

    def set_migration_dir(self, migration_dir):
        self.migration_dir = migration_dir

    def get_migration_dir(self):
        return self.migration_dir

    def set_endpoint(self, endpoint):
        self.base_endpoint = endpoint

    def get_base_endpoint(self):
        return self.base_endpoint

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = Fetcher.Fetcher(self.config)
        return self.fetcher

    def get_endpoint(self):
        return '_'.join((self.datatype, self.action))


    def process_data(self, action):
        file_name = "_".join((self.get_base_endpoint(), action))
        if os.path.exists(self.migration_dir+"/"+file_name) is False:
            return False

        with open(self.migration_dir+"/"+file_name, 'r') as reader:
            self.set_data({'old': ast.literal_eval(reader.read())})

        storage_dir = '/'.join((self.get_migration_dir(), self.get_endpoint()))
        if os.path.exists(storage_dir) is False:
            os.mkdir(storage_dir)

        fetcher = self.get_fetcher()
        for item in self.get_data()['old']:
            print("Fetching \""+item+"\" in datatype \""+self.datatype+"\".")
            fetch_item = fetcher.fetch(self.get_endpoint(), {'id': item})
            print("Fetched \""+item+"\" successfully.")
            f = self.init_file('/'.join((self.get_migration_dir(), self.get_endpoint(), item+".json")))
            f.write(json.dumps(fetch_item))
            f.close()
        print("All files were successfully downloaded. Started parsing …")
        self.parse_data()

    def parse_data(self):
        for item in self.get_data()['old']:
            print("Parsing \""+item+"\" in datatype \""+self.datatype+"\".")
            old_json = None
            with open('/'.join((self.get_migration_dir(), self.get_endpoint(), item+".json")), 'r') as reader:
                old_json = json.loads(reader.read())

            if old_json is None:
                return False

            new_json = self.process_json(old_json)
            self.validate_json(new_json)
            f = self.init_file('/'.join((self.get_migration_dir(), self.get_endpoint(), item+"_new.json")))
            f.write(json.dumps(new_json))
            f.close()

            print("Saved item successfully \""+item+"\" successfully.")
        print("All files were successfully parsed into new files. You can download them in: "+'/'.join((os.getcwd(), self.migration_dir)))


    def process_json(self, old_json):
        new_json = {'@context': 'https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld', 'iri': "https://data.gov.cz/lkod/mdcr/datové-sady/vld", 'typ': 'Datová sada'}
        new_json['název'] = {'cs': old_json['title']}
        resource = old_json['resources'][0]
        new_json['popis'] = {'cs': resource['name']}
        new_json['dokumentace'] = 'https://operator-ict.gitlab.io/golemio/documentation'
        new_json['prvek_rúian'] = 'https://linked.cuzk.cz/resource/ruian/stat/1'
        new_json['poskytovatel'] = '/'.join(('https://linked.opendata.cz/zdroj/ekonomický-subjekt/', self.config.vatin))
        new_json['periodicita_aktualizace'] = 'http://publications.europa.eu/resource/authority/frequency/MONTHLY'
        new_json['časové_pokrytí'] = {
            'typ': 'Časový interval',
            'začátek': datetime.strptime(resource['created']),
            'konec': datetime.strptime(resource['last_modified'])
        }
        new_json['distribuce'] = [{
            'typ_média': 'http://www.iana.org/assignments/media-types/'+resource['mimetype'],
            'typ': 'Distribuce',
            'název': {
                'cs': resource['name']
            },
            'soubor_ke_stažení': resource['url'],
            'přístupové_url': resource['url'],
            'formát': 'http://publications.europa.eu/resource/authority/file-type/'+resource['format']
        }]
        self.validate_json(new_json)
        return new_json

    def validate_json(self, json_to_validate):
        ...

    def init_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w")
        return f

    def write_output(self, string):
        sys.stdout.write(string+"\r")
        sys.stdout.flush()
        time.sleep(1)