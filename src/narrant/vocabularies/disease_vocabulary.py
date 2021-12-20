from narrant.config import DISEASE_TAGGER_VOCAB_DIRECTORY
from narrant.vocabularies.generic_vocabulary import GenericVocabulary


class DiseaseVocabulary:

    @staticmethod
    def create_disease_vocabulary(expand_by_s_and_e=True):
        return GenericVocabulary.create_vocabulary_from_directory(DISEASE_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)
