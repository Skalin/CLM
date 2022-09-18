from enum import Enum

class MigrationVariant(Enum):
    ALL = 'all'
    VALID = 'valid'
    INVALID = 'invalid'

    def labels(self):
        return {
            self.ALL.value: 'Vše',
            self.VALID.value: 'Pouze validní',
            self.INVALID.value: 'Pouze nevalidní'
        }

    def label(self):
        return self.labels()[self.value] if self.value in self.labels() else ''