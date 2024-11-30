from narrant import config
from narrant.entitylinking import enttypes
from narrant.entitylinking.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.cellline_vocabulary import CellLineVocabulary


class CellLineTagger(IndexedDictTagger):
    TYPES = (enttypes.CELLLINE,)
    __name__ = "CellLineTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("cellline", "CellLineTagger", CellLineTagger.__version__,
                         enttypes.CHEMICAL, config.CELL_LINE_VOCAB_DIRECTORY, *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = CellLineVocabulary.create_cell_line_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} Cell Line terms found in database')
