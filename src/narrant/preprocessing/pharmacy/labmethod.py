from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.labmethod_vocabulary import LabMethodVocabulary


class LabMethodTagger(IndexedDictTagger):
    TYPES = (enttypes.METHOD,)
    __name__ = "LabMethodTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("labmethod", "LabMethodTagger", LabMethodTagger.__version__,
                         enttypes.LAB_METHOD, config.METHOD_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = LabMethodVocabulary.create_lab_method_vocabulary(self.source)
        self.logger.info(f'{len(self.desc_by_term)} Lab Method terms found in database')
