from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.target_vocabulary import TargetVocabulary


class TargetTagger(IndexedDictTagger):
    TYPES = (enttypes.TARGET,)
    __name__ = "TargetTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("target", "TargetTagger", TargetTagger.__version__,
                         enttypes.TARGET, config.TARGET_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = TargetVocabulary.create_target_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} target terms found in sources')
