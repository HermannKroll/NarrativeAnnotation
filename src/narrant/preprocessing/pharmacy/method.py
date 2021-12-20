from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.dictagger import DictTagger
from narrant.vocabularies.method_vocabulary import MethodVocabulary


class MethodTagger(DictTagger):
    TYPES = (enttypes.METHOD,)
    __name__ = "MethodTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("method", "MethodTagger", MethodTagger.__version__,
                         enttypes.METHOD, config.METHOD_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = MethodVocabulary.create_method_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} Method terms found in database')
