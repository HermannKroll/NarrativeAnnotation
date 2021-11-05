from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.dictagger import DictTagger
from narrant.preprocessing.tagging.vocabularies import ExcipientVocabulary


class ExcipientTagger(DictTagger):
    TYPES = (enttypes.EXCIPIENT,)
    __name__ = "ExcipientTagger"
    __version__ = "2.1.0"

    def __init__(self, *args, **kwargs):
        super().__init__("excipient", "ExcipientTagger", ExcipientTagger.__version__,
                         enttypes.EXCIPIENT, config.EXCIPIENT_TAGGER_INDEX_CACHE, config.EXCIPIENT_TAGGER_DATABASE_FILE,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Reading drugbank database for DrugBank mapping...')
        self.desc_by_term = ExcipientVocabulary.create_excipient_vocabulary()

        new_excipients, drugbank_mappings_found = 0, 0
        for term, descs in self.desc_by_term.items():
            for d in descs:
                if d.startswith('CHEMBL'):
                    drugbank_mappings_found += 1
                else:
                    new_excipients += 1
        self.logger.info(
            f'{drugbank_mappings_found} excipients could be mapped to Chebml. {new_excipients} are not in Chebml')
        self.logger.info(f'{len(self.desc_by_term)} excipients found in database')
