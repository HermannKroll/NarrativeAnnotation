from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.dictagger import DictTagger
from narrant.preprocessing.tagging.vocabularies import ChemicalVocabulary


class ChemicalTagger(DictTagger):
    TYPES = (enttypes.CHEMICAL,)
    __name__ = "ChemicalTagger"
    __version__ = "2.1.0"

    def __init__(self, *args, **kwargs):
        super().__init__("chemical", "ChemicalTagger", ChemicalTagger.__version__,
                         enttypes.CHEMICAL, config.CHEMBL_CHEMICAL_INDEX_CACHE, config.CHEMBL_CHEMICAL_DATABASE_FILE,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = ChemicalVocabulary.create_chembl_chemical_vocabulary(chemical_list=self.source_file)
        self.logger.info(f'{len(self.desc_by_term)} Chembl chemicals found in database')
