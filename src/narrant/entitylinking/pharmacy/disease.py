from narrant import config
from narrant.entitylinking import enttypes
from narrant.entitylinking.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.disease_vocabulary import DiseaseVocabulary


class DiseaseTagger(IndexedDictTagger):
    TYPES = (enttypes.DISEASE,)
    __name__ = "DiseaseTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("disease", "DiseaseTagger", DiseaseTagger.__version__,
                         enttypes.DISEASE, config.DISEASE_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = DiseaseVocabulary.create_disease_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} Disease terms found in database')
