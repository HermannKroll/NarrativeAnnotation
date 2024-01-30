from narrant import config
from narrant.entitylinking import enttypes
from narrant.entitylinking.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.tissue_vocabulary import TissueVocabulary


class TissueTagger(IndexedDictTagger):
    TYPES = (enttypes.TISSUE,)
    __name__ = "TissueTagger"
    __version__ = "1.2.0"

    def __init__(self, *args, **kwargs):
        super().__init__("tissue", "TissueTagger", TissueTagger.__version__,
                         enttypes.TISSUE, config.TISSUE_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = TissueVocabulary.create_tissue_vocabulary(expand_by_s_and_e=True)
        self.logger.info(f'{len(self.desc_by_term)} target terms found in sources')
