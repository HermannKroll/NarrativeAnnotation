from narrant import config
from narrant.entitylinking import enttypes
from narrant.entitylinking.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.organism_vocabulary import OrganismVocabulary


class OrganismTagger(IndexedDictTagger):
    TYPES = (enttypes.ORGANISM,)
    __name__ = "OrganismTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("organism", "OrganismTagger", OrganismTagger.__version__,
                         enttypes.ORGANISM, config.ORGANISM_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = OrganismVocabulary.create_organism_vocabulary(expand_by_s_and_e=True)
        self.logger.info(f'{len(self.desc_by_term)} target terms found in sources')
