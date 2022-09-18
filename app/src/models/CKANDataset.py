
from mimetypes import init


class CKANDataset():
    name =  ''
    data = {}
    fetcher = None

    def __init__(self, fetcher, dataset) -> None:
        self.fetcher = fetcher
        self.name = dataset
        self.data = self.fetcher.fetch('package_show', {'id': self.name})