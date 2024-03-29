from narrant import config
from narrant.entitylinking import enttypes
from narrant.entitylinking.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.vaccine_vocabulary import VaccineVocabulary


class VaccineTagger(IndexedDictTagger):
    TYPES = (enttypes.VACCINE,)
    __name__ = "VaccineTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("vaccine", "VaccineTagger", VaccineTagger.__version__,
                         enttypes.VACCINE, config.VACCINE_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = VaccineVocabulary.create_vaccine_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} vaccine terms found in sources')
