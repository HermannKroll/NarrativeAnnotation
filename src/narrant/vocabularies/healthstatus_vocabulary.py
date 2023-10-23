from narrant.config import HEALTH_STATUS_TAGGER_VOCAB_DIRECTORY
from narrant.vocabularies.generic_vocabulary import GenericVocabulary


class HealthStatusVocabulary:

    @staticmethod
    def create_health_status_vocabulary(expand_by_s_and_e=True):
        return GenericVocabulary.create_vocabulary_from_directory(HEALTH_STATUS_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)
