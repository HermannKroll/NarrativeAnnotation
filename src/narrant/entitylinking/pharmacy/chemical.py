from narrant import config
from narrant.entitylinking import enttypes
from narrant.entitylinking.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.chemical_vocabulary import ChemicalVocabulary


class ChemicalTagger(IndexedDictTagger):
    TYPES = (enttypes.CHEMICAL,)
    __name__ = "ChemicalTagger"
    __version__ = "2.1.0"

    def __init__(self, *args, **kwargs):
        super().__init__("chemical", "ChemicalTagger", ChemicalTagger.__version__,
                         enttypes.CHEMICAL, config.CHEMBL_CHEMICAL_DATABASE_FILE,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = ChemicalVocabulary.create_chembl_chemical_vocabulary(chemical_list=self.source)
        self.logger.info(f'{len(self.desc_by_term)} Chembl chemicals found in database')
