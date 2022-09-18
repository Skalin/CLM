from enum import Enum

class DatasetStatus(Enum):

    VALID = 'valid'
    INVALID = 'invalid'

    def labels(self):
        return {
            self.VALID.value: 'Plně zmigrovatelné',
            self.INVALID.value: 'Zmigrovatelné s úpravami'
        }

    def label(self):
        return self.labels()[self.value] if self.value in self.labels() else ''
