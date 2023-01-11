import logging
import os

from narrant.config import TISSUE_TAGGER_VOCAB, TISSUE_TAGGER_VOCAB_DIRECTORY
from narrant.preprocessing.enttypes import TISSUE
from narrant.vocabularies.generic_vocabulary import GenericVocabulary
from narrant.vocabularies.target_vocabulary import TargetVocabulary


class TissueVocabulary(TargetVocabulary):

    def __init__(self):
        super().__init__(TISSUE_TAGGER_VOCAB, entity_type_in_vocab=TISSUE)
        self.ignored_target_types = {}
        self.allowed_target_types = {'TISSUE'}

    @staticmethod
    def create_tissue_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(TISSUE_TAGGER_VOCAB):
            TissueVocabulary().initialize_vocabulary()

        return GenericVocabulary.create_vocabulary_from_directory(TISSUE_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    TissueVocabulary().initialize_vocabulary(force_create=True)
