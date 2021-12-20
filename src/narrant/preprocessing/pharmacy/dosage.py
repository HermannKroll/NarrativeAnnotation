from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.dictagger import DictTagger
from narrant.vocabularies.dosageform_vocabulary import DosageFormVocabulary


class DosageFormTagger(DictTagger):
    TYPES = (enttypes.DOSAGE_FORM,)
    __name__ = "DosageFormTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("dosage", "DosageFormTagger", DosageFormTagger.__version__,
                         enttypes.DOSAGE_FORM, config.DOSAGEFORM_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = DosageFormVocabulary.create_dosage_form_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} DosageForm terms found in database')
