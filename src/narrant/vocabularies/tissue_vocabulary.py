from narrant.config import TISSUE_TAGGER_VOCAB_DIRECTORY
from narrant.vocabularies.generic_vocabulary import GenericVocabulary
from narrant.vocabularies.target_vocabulary import TargetVocabulary


class TissueVocabulary(TargetVocabulary):

    @staticmethod
    def create_tissue_vocabulary(expand_by_s_and_e=True):
        return GenericVocabulary.create_vocabulary_from_directory(TISSUE_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)
