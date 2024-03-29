from narrant.config import VACCINE_TAGGER_VOCAB_DIRECTORY
from narrant.vocabularies.generic_vocabulary import GenericVocabulary


class VaccineVocabulary:

    @staticmethod
    def create_vaccine_vocabulary(expand_by_s_and_e=True):
        return GenericVocabulary.create_vocabulary_from_directory(VACCINE_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)
